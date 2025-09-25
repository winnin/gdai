import asyncio
import json
import os
import uuid

import aiofiles
from aiopath import AsyncPath
from temporalio import activity

from gdai.chunkers import ChunkerFactory
from gdai.commons.config import Config
from gdai.commons.enums import ChunkTypeEnum, DocumentTypeEnum
from gdai.commons.logger import logger
from gdai.extractors import ExtractorFactory
from gdai.repositories import RepositoryFactory
from gdai.repositories.models import ChunkModel, DocumentModel

from .schema import Chunk, ChunkDocumentInput, DocumentExtracInput, StoreDocumentInput, TempFiles


@activity.defn
async def validate(input: DocumentExtracInput) -> None:
    tenant_id = input.tenant_id
    document_path = input.document_path

    # validate tenant_id
    if not tenant_id or not isinstance(tenant_id, str):
        logger.error("Invalid tenant_id provided")
        raise ValueError("Invalid tenant_id provided")

    # check if document exists
    if not await AsyncPath(document_path).exists():
        logger.error(f"Document file does not exist: {document_path}")
        raise FileNotFoundError(f"Document file does not exist: {document_path}")

    # check if document max size is not exceeded
    file_size = (await AsyncPath(document_path).stat()).st_size

    # check if document is empty
    if file_size == 0:
        logger.error(f"Document file is empty: {document_path}")
        raise ValueError(f"Document file is empty: {document_path}")

    # check if document exceeds maximum size
    if file_size > Config.extractor.MAX_FILE_SIZE_MB * 1024 * 1024:  # configured limit in MB
        logger.error(f"Document file {document_path} exceeds maximum allowed size")
        raise ValueError(f"Document file {document_path} exceeds maximum allowed size")

    logger.info(f"Document validation completed for: {document_path}")


@activity.defn
async def extract(input: DocumentExtracInput) -> str:
    document_path = input.document_path
    document_extension = document_path.split(".")[-1].lower()  # get document extension

    logger.info(f"Starting document extraction for: {document_path} (type: {document_extension})")

    extractor = ExtractorFactory.get_extractor(extractor_type=document_extension)
    try:
        extracted_document = extractor.extract_document_data(document_path)
        output_file = os.path.join(Config.extractor.TMP_FOLDER, f"{uuid.uuid4()}.json")
        async with aiofiles.open(output_file, "w") as f:
            await f.write(json.dumps(extracted_document))

        logger.info(f"Document extraction completed. Output saved to: {output_file}")
        return output_file
    except Exception as e:
        logger.error(f"Error extracting data from document: {e}")
        raise e


@activity.defn
async def chunk_texts(input: ChunkDocumentInput) -> list[str]:
    chunk_strategy = input.chunk_strategy
    extracted_document_path = input.extracted_document_path

    logger.info(f"Starting text chunking with strategy: {chunk_strategy}")
    logger.debug(f"Processing document: {extracted_document_path}")

    async with aiofiles.open(extracted_document_path) as f:
        extracted_document = json.loads(await f.read())

    chunker = ChunkerFactory.get_chunker(chunker_type=chunk_strategy)
    only_text_by_page = [item[1] for item in extracted_document["texts"]]
    doc_text_chunks = chunker.chunk(only_text_by_page)
    chunks = []

    for page_number, text_content in doc_text_chunks:
        chunk = Chunk(
            id=str(uuid.uuid4()),
            type="text",
            chunk=text_content,
            page_number=page_number,
        )
        chunks.append(chunk)

    logger.info(f"Generated {len(chunks)} chunks from document")

    batch_size = Config.embedding.BATCH_SIZE
    chunks_batch = [chunks[i : i + batch_size] for i in range(0, len(chunks), batch_size)]
    chunk_files = []

    logger.info(f"Creating {len(chunks_batch)} chunk files with batch size: {batch_size}")

    for idx, batch in enumerate(chunks_batch):
        chunks_str = json.dumps([chunk.__dict__ for chunk in batch], indent=2)
        chunk_file_path = extracted_document_path.replace(".json", f"_chunks_{idx}.json")
        with open(chunk_file_path, "w") as f:
            f.write(chunks_str)
            chunk_files.append(chunk_file_path)
        logger.debug(f"Created chunk file {idx + 1}/{len(chunks_batch)}: {chunk_file_path}")

    logger.info(f"Text chunking completed. Created {len(chunk_files)} chunk files")
    return chunk_files


@activity.defn
async def store_embedded_chunks(input: StoreDocumentInput) -> None:
    tenant_id = input.tenant_id
    chunk_strategy = input.chunk_strategy
    document_original_path = input.document_original_path
    document_chunks_path = input.document_chunks_path

    logger.info(f"Starting storage of embedded chunks for document: {document_original_path}")
    logger.debug(f"Tenant: {tenant_id}, Chunk strategy: {chunk_strategy}")

    repository = RepositoryFactory.get_repository()

    # insert document data
    document_name = document_original_path.split("/")[-1]
    document_type = document_name.split(".")[-1].lower()
    document_id = uuid.uuid4()
    document_model = DocumentModel(
        id=document_id,
        name=document_name,
        tenant_id=tenant_id,
        type=DocumentTypeEnum[document_type],
        chunk_strategy=chunk_strategy,
    )

    try:
        await repository.insert_document(document_model)
        logger.info(f"Document {document_name} inserted with ID: {document_id}")
    except Exception as e:
        logger.error(f"Error inserting document into database: {e}")
        raise e

    # insert chunks data
    async with aiofiles.open(document_chunks_path) as f:
        # if chunks is empty list, do not insert and add status to document as failed do chunk
        document_chunks = json.loads(await f.read())

        if not document_chunks:
            logger.warning(f"No chunks found in file: {document_chunks_path}")
            return

        logger.info(f"Processing {len(document_chunks)} chunks for storage")

        chunk_models = [
            ChunkModel(
                id=uuid.UUID(chunk["id"]),
                tenant_id=tenant_id,
                type=ChunkTypeEnum[chunk["type"]],
                chunk=chunk["chunk"],
                page_number=chunk["page_number"],
                document_id=document_id,
                embedding=chunk["embedding"],
            )
            for chunk in document_chunks
        ]

        try:
            await repository.insert_chunks(chunk_models)
            logger.info(f"Successfully stored {len(chunk_models)} chunks for document {document_name}")
        except Exception as e:
            logger.error(f"Error inserting chunks into the database: {e}")
            raise e


@activity.defn
async def remove_temp_files(files_to_remove: TempFiles) -> None:
    logger.info("Starting cleanup of temporary files")

    files_to_remove_list = (
        [files_to_remove.extracted_document_file_path] + files_to_remove.chunk_files + files_to_remove.embedded_files
    )

    logger.debug(f"Removing {len(files_to_remove_list)} temporary files")

    async def remove_single_file(file_path):
        try:
            if await AsyncPath(file_path).exists():
                await AsyncPath(file_path).unlink()
                logger.debug(f"Removed temporary file: {file_path}")
            else:
                logger.warning(f"Temporary file not found, could not remove: {file_path}")
        except Exception as e:
            logger.error(f"Error removing temporary file {file_path}: {e}")

    # Execute all removal operations in parallel
    await asyncio.gather(*[remove_single_file(file_path) for file_path in files_to_remove_list])

    logger.info("Temporary files cleanup completed")
