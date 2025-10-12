import asyncio
import json
import os
import uuid

import aiofiles
from aiopath import AsyncPath
from temporalio import activity

from gdai.chunkers import ChunkerFactory
from gdai.commons.enums import ChunkTypeEnum, DocumentTypeEnum
from gdai.commons.logger import logger
from gdai.commons.settings import get_settings
from gdai.extractors import ExtractorFactory
from gdai.repositories import RepositoryFactory
from gdai.repositories.models import ChunkModel, DocumentModel
from gdai.services.s3_storage import get_s3_storage

from .schema import Chunk, ChunkDocumentInput, DocumentExtracInput


@activity.defn
async def validate(input: DocumentExtracInput) -> None:
    tenant_id = input.tenant_id
    s3_key = input.s3_key

    # validate tenant_id
    if not tenant_id or not isinstance(tenant_id, str):
        logger.error("Invalid tenant_id provided")
        raise ValueError("Invalid tenant_id provided")

    # validate s3_key
    if not s3_key or not isinstance(s3_key, str):
        logger.error("Invalid s3_key provided")
        raise ValueError("Invalid s3_key provided")

    # check if document exists in S3
    s3_storage = get_s3_storage()
    if not s3_storage.file_exists(s3_key):
        logger.error(f"Document file does not exist in S3: {s3_key}")
        raise FileNotFoundError(f"Document file does not exist in S3: {s3_key}")

    # get file metadata to check size
    try:
        response = s3_storage.client.head_object(Bucket=s3_storage.bucket, Key=s3_key)
        file_size = response["ContentLength"]

        # check if document is empty
        if file_size == 0:
            logger.error(f"Document file is empty: {s3_key}")
            raise ValueError(f"Document file is empty: {s3_key}")

        # check if document exceeds maximum size
        settings = get_settings()
        max_file_size_mb = settings.extractor.max_file_size_mb
        if file_size > max_file_size_mb * 1024 * 1024:  # configured limit in MB
            logger.error(f"Document file {s3_key} exceeds maximum allowed size")
            raise ValueError(f"Document file {s3_key} exceeds maximum allowed size")

        logger.info(f"Document validation completed for S3 file: {s3_key}")
    except Exception as e:
        logger.error(f"Error validating document in S3: {e}")
        raise


@activity.defn
async def save_document_metadata(input: DocumentExtracInput) -> str:
    tenant_id = input.tenant_id
    s3_key = input.s3_key
    document_name = s3_key.split("/")[-1]  # Extract filename from S3 key
    document_type = document_name.split(".")[-1].lower()
    chunk_strategy = input.chunk_strategy

    logger.info(f"Saving document metadata for S3 file: {s3_key}")
    logger.debug(f"Tenant: {tenant_id}, Document type: {document_type}, Chunk strategy: {chunk_strategy}")

    document_id = uuid.uuid4()
    document_model = DocumentModel(
        id=document_id,
        name=document_name,
        tenant_id=tenant_id,
        type=DocumentTypeEnum[document_type],
        s3_path=s3_key,
        chunk_strategy=chunk_strategy,
    )

    try:
        async with RepositoryFactory.get_repository() as repository:
            await repository.insert_document(document_model)
        logger.info(f"Document {document_name} metadata saved with ID: {document_id}")
        return str(document_id)
    except Exception as e:
        logger.error(f"Error saving document metadata to database: {e}")
        raise e


@activity.defn
async def extract_document_content(input: DocumentExtracInput) -> str:
    s3_key = input.s3_key
    document_extension = s3_key.split(".")[-1].lower()  # get document extension

    logger.info(f"Starting document extraction for S3 file: {s3_key} (type: {document_extension})")

    # Download file from S3 to temporary location
    settings = get_settings()
    tmp_folder = settings.extractor.tmp_folder
    local_file_path = os.path.join(tmp_folder, f"{uuid.uuid4()}.{document_extension}")

    s3_storage = get_s3_storage()
    try:
        # Download from S3
        s3_storage.download_file(s3_key, local_file_path)
        logger.info(f"Downloaded document from S3 to: {local_file_path}")

        # Extract content
        extractor = ExtractorFactory.get_extractor(extractor_type=document_extension)
        extracted_document = extractor.extract_document_data(local_file_path)

        # Save extracted content to JSON
        output_file = os.path.join(tmp_folder, f"{uuid.uuid4()}.json")
        async with aiofiles.open(output_file, "w") as f:
            await f.write(json.dumps(extracted_document))

        # Clean up downloaded file
        await AsyncPath(local_file_path).unlink()

        logger.info(f"Document extraction completed. Output saved to: {output_file}")
        return output_file
    except Exception as e:
        # Clean up on error
        if await AsyncPath(local_file_path).exists():
            await AsyncPath(local_file_path).unlink()
        logger.error(f"Error extracting data from document: {e}")
        raise e


@activity.defn
async def chunk_texts_to_batched_files(input: ChunkDocumentInput) -> list[str]:
    chunk_strategy = input.chunk_strategy
    extracted_document_path = input.extracted_document_path

    logger.info(f"Starting text chunking with strategy: {chunk_strategy}")
    logger.debug(f"Processing document: {extracted_document_path}")

    # load extracted document
    async with aiofiles.open(extracted_document_path) as f:
        extracted_document = json.loads(await f.read())

    # chunk texts
    chunker = ChunkerFactory.get_chunker(chunker_type=chunk_strategy)
    only_text_by_page = [item[1] for item in extracted_document["texts"]]
    doc_text_chunks = chunker.chunk(only_text_by_page)
    chunks = []

    # create chunk objects
    for page_number, text_content in doc_text_chunks:
        chunk = Chunk(
            id=str(uuid.uuid4()),
            tenant_id=input.tenant_id,
            document_id=input.document_id,
            type="text",  # TODO: dynamic based on content
            chunk=text_content,
            page_number=page_number,
        )
        chunks.append(chunk)

    # create batched chunk files
    logger.info(f"Generated {len(chunks)} chunks from document")
    settings = get_settings()
    batch_size = settings.embedding.batch_size
    batches = [chunks[i : i + batch_size] for i in range(0, len(chunks), batch_size)]

    generated_files = []
    for idx, batch in enumerate(batches):
        logger.info(f"Processing a batch of {len(batch)} chunks")
        chunks_str = json.dumps([chunk.__dict__ for chunk in batch], indent=2)
        chunk_file_path = extracted_document_path.replace(".json", f"_chunks_{idx}.json")
        generated_files.append(chunk_file_path)
        async with aiofiles.open(chunk_file_path, "w") as f:
            await f.write(chunks_str)

    logger.info("Text chunking completed. ")
    return generated_files


@activity.defn
async def get_chunk_file_content_for_embedding(chunk_file_path: str) -> list[list[dict]]:
    logger.info(f"Loading chunks from file for embedding: {chunk_file_path}")
    async with aiofiles.open(chunk_file_path) as f:
        document_chunks = json.loads(await f.read())

    if not document_chunks:
        logger.warning(f"No chunks found in file: {chunk_file_path}")
        return []

    logger.info(f"Loaded {len(document_chunks)} chunks from file: {chunk_file_path}")
    return document_chunks


@activity.defn
async def store_embedded_chunks(input: list[Chunk]) -> None:
    if not input:
        logger.warning("No chunks provided for storage")
        return

    chunk_models = [
        ChunkModel(
            id=chunk.id,
            tenant_id=chunk.tenant_id,
            document_id=chunk.document_id,
            type=ChunkTypeEnum[chunk.type],
            chunk=chunk.chunk,
            page_number=chunk.page_number,
            embedding=chunk.embedding,
        )
        for chunk in input
    ]

    try:
        async with RepositoryFactory.get_repository() as repository:
            await repository.insert_batch_chunks(chunk_models)
        logger.info(f"Stored {len(chunk_models)} chunks into the database")
    except Exception as e:
        logger.error(f"Error storing chunks into database: {e}")
        raise e


@activity.defn
async def remove_temp_files(files_to_remove: list[str]) -> None:
    logger.info("Starting cleanup of temporary files")
    logger.debug(f"Removing {len(files_to_remove)} temporary files")

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
    await asyncio.gather(*[remove_single_file(file_path) for file_path in files_to_remove])

    logger.info("Temporary files cleanup completed")
