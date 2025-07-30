from __future__ import annotations

import asyncio
from time import time

from gdai.background_tasks.embedding_background_task import embedding_document
from gdai.chunkers import ChunkerFactory
from gdai.config.broker import dramatiq  # with broked configured
from gdai.config.logger import logger
from gdai.config.settings import Config
from gdai.extractors import ExtractorFactory
from gdai.repositories import RepositoryFactory
from gdai.services.document_service import ExtractDocumentService


@dramatiq.actor(
    queue_name=Config.extractor.QUEUE,
    max_retries=Config.extractor.MAX_RETRIES,
    min_backoff=Config.extractor.RETRY_DELAY,
)
def document_extractor(document_data: dict):
    """Extract text from a document and prepare it for embedding processing."""
    try:
        logger.info(f"Received document data: {document_data}")

        # Validate document_path
        document_path = document_data.get("document_path")
        if not document_path:
            logger.error("Document path is required")
            raise ValueError("Document path is required")

        # Validate tenant_id
        tenant_id = document_data.get("tenant_id")
        if not tenant_id:
            logger.error("Tenant ID is required")
            raise ValueError("Tenant ID is required")

        # Start the document extraction process
        try:
            logger.info(f"Beginning document extraction for  {document_path}")
            start_time = time()
            document_extension = document_path.split(".")[-1].lower()
            document_extractor = ExtractorFactory.get_extractor(extractor_type=document_extension)
            repository = RepositoryFactory.get_repository()
            chunker = ChunkerFactory.get_chunker(chunker_type="sentence")  # TODO: change chunker by type
            service = ExtractDocumentService(repository, document_extractor, chunker)
            document = asyncio.run(service.extract_data_from_document(tenant_id, document_path))
            logger.info(f"Document extraction completed for {document_path}")
            process_time = time() - start_time
            logger.info(f"Document extraction for {document_path} completed successfully in {process_time:.2f}s")
        except Exception as e:
            logger.error(f"Failed to extract document {document_path}: {e!s}")
            raise

        try:
            embedding_document.send(
                {"document_path": document_path, "tenant_id": tenant_id, "document_id": str(document.id)}
            )  # call next action
            logger.info(f"Document {document.name} sent for embedding processing")
        except Exception as e:
            logger.error(f"Failed to enqueue document for embedding: {e!s}")
            raise

    except Exception as e:
        logger.error(f"Failed to extract document {document_data}: {e!s}")
        raise
