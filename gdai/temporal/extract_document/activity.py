import json
import os
import uuid

from temporalio import activity

from gdai.chunkers import ChunkerFactory
from gdai.commons.config import Config
from gdai.commons.enums import ChunkTypeEnum, DocumentTypeEnum
from gdai.commons.logger import logger
from gdai.extractors import ExtractorFactory
from gdai.repositories import RepositoryFactory
from gdai.repositories.models import ChunkModel, DocumentModel

from .schema import Chunk, ChunkDocumentInput, DocumentExtracInput, StoreDocumentInput


@activity.defn
async def validate(input: DocumentExtracInput) -> None:
    tenant_id = input.tenant_id
    document_path = input.document_path

    # validate tenant_id
    if not tenant_id or not isinstance(tenant_id, str):
        logger.error("Invalid tenant_id provided")
        raise ValueError("Invalid tenant_id provided")

    # check if document exists
    if not os.path.exists(document_path):
        logger.error(f"Document file does not exist: {document_path}")
        raise FileNotFoundError(f"Document file does not exist: {document_path}")

    # check if document is readable
    if not os.access(document_path, os.R_OK):
        logger.error(f"Document file is not readable: {document_path}")
        raise PermissionError(f"Document file is not readable: {document_path}")

    # check if document max size is not exceeded
    file_size = os.path.getsize(document_path)

    # check if document is empty
    if file_size == 0:
        logger.error(f"Document file is empty: {document_path}")
        raise ValueError(f"Document file is empty: {document_path}")

    # check if document exceeds maximum size
    if file_size > Config.extractor.MAX_FILE_SIZE_MB * 1024 * 1024:  # configured limit in MB
        logger.error(f"Document file {document_path} exceeds maximum allowed size")
        raise ValueError(f"Document file {document_path} exceeds maximum allowed size")


@activity.defn
async def extract(input: DocumentExtracInput) -> str:
    document_path = input.document_path
    document_extension = document_path.split(".")[-1].lower()  # get document extension
    extractor = ExtractorFactory.get_extractor(extractor_type=document_extension)
    try:
        extracted_document = extractor.extract_document_data(document_path)
        output_file = os.path.join(Config.extractor.TMP_FOLDER, f"{uuid.uuid4()}.json")
        with open(output_file, "w") as f:
            json.dump(extracted_document, f)
        return output_file
    except Exception as e:
        logger.error(f"Error extracting data from document: {e}")
        raise e


@activity.defn
async def chunk_texts(input: ChunkDocumentInput) -> str:
    chunk_strategy = input.chunk_strategy
    extracted_document_path = input.extracted_document_path
    with open(extracted_document_path) as f:
        extracted_document = json.load(f)
    chunker = ChunkerFactory.get_chunker(chunker_type=chunk_strategy)
    only_text_by_page = [item[1] for item in extracted_document["texts"]]
    doc_text_chunks = chunker.chunk(only_text_by_page)
    chunks = []
    for page_number, text_content in doc_text_chunks:
        chunk = Chunk(
            type="text",
            chunk=text_content,
            page_number=page_number,
        )
        chunks.append(chunk)
    chunks_str = json.dumps([chunk.__dict__ for chunk in chunks], indent=2)
    chunk_file_path = extracted_document_path.replace(".json", "_chunks.json")
    with open(chunk_file_path, "w") as f:
        f.write(chunks_str)
    return chunk_file_path


@activity.defn
async def store(input: StoreDocumentInput) -> None:
    tenant_id = input.tenant_id
    chunk_strategy = input.chunk_strategy
    document_original_path = input.document_original_path
    document_chunks_path = input.document_chunks_path

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
    await repository.insert_document(document_model)

    # insert chunks data
    with open(document_chunks_path) as f:
        # if chunks is empty list, do not insert and add status to document as failed do chunk

        document_chunks = json.load(f)
        chunk_models = [
            ChunkModel(
                type=ChunkTypeEnum[chunk["type"]],
                chunk=chunk["chunk"],
                page_number=chunk["page_number"],
                document_id=document_id,
            )
            for chunk in document_chunks
        ]
        await repository.insert_chunks(chunk_models)
