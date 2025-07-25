from __future__ import annotations

import os

from gdai.config.broker import dramatiq  # with broked configured
from gdai.config.logger import logger
from gdai.config.settings import Config
from gdai.services.document import ExtractDocumentService

from .embedding_chunks import embedding_document

service = ExtractDocumentService()


@dramatiq.actor(
    queue_name=Config.extractor.QUEUE,
    max_retries=Config.extractor.MAX_RETRIES,
    min_backoff=Config.extractor.RETRY_DELAY,
)
def document_extractor(document_data: dict):
    """Dramatiq actor for extracting document data.
    Receives document metadata, validates and processes the file, extracts content, saves the result, and triggers
    embedding.

    Args:
        document_data (dict): Dictionary with 'document_name' and 'tenant_id'.

    Raises:
        ValueError, FileNotFoundError, PermissionError, IOError: On various file and processing errors.
    """
    try:
        logger.info(f"Received document data: {document_data}")
        document_name = document_data.get("document_name")

        # Validate document name
        if not document_name:
            logger.error("Document name is required")
            raise ValueError("Document name is required")

        # Validate tenant ID a
        tenant_id = document_data.get("tenant_id")
        if not tenant_id:
            logger.error("Tenant ID is required")
            raise ValueError("Tenant ID is required")

        # Construct the full document path
        folder_path = os.path.join(Config.extractor.FOLDER_RAW_DOC_PATH, tenant_id)
        document_full_path = os.path.join(folder_path, document_name)

        # Start the document extraction process
        try:
            logger.info(f"Beginning document extraction for {document_name} at {document_full_path}")
            document = service.extract_data_from_document(tenant_id, document_full_path)
            logger.info(f"Document extraction completed for {document_name}")
        except Exception as e:
            logger.error(f"Failed to extract document {document_name}: {e!s}")
            raise
        # Send to next stage with error handling
        try:
            embedding_document.send({"document_path": document.name})  # call next action
            logger.info(f"Document {document.name} sent for embedding processing")
        except Exception as e:
            logger.error(f"Failed to enqueue document for embedding: {e!s}")
            raise

    except Exception as e:
        logger.error(f"Failed to extract document {document_data}: {e!s}")
        raise
