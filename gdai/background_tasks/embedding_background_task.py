import asyncio
from time import time

from gdai.config.broker import dramatiq
from gdai.config.logger import logger
from gdai.config.settings import Config
from gdai.embeddings import EmbeddingFactory
from gdai.repositories import RepositoryFactory
from gdai.services.embedding_service import EmbeddingDocumentService


@dramatiq.actor(
    queue_name=Config.embedding.QUEUE,
    max_retries=Config.embedding.MAX_RETRIES,
    min_backoff=Config.embedding.RETRY_DELAY,
)
def embedding_document(document_data: dict):
    try:
        logger.info(f"Received document data: {document_data}")

        # Validate document_id
        document_id = document_data.get("document_id")
        if not document_id:
            logger.error("document_id is required")
            raise ValueError("document_id is required")

        # Validate tenant_id
        tenant_id = document_data.get("tenant_id")
        if not tenant_id:
            logger.error("tenant_id is required")
            raise ValueError("tenant_id is required")

        try:
            logger.info(f"Beginning embedding for document_id {document_id}")
            start_time = time()
            embedding_model = asyncio.run(EmbeddingFactory.get_embedding())
            repository = RepositoryFactory.get_repository()
            service = EmbeddingDocumentService(embedding_model=embedding_model, repository=repository, batch_size=64)
            asyncio.run(service.process_document(tenant_id, document_id))
            process_time = time() - start_time
            logger.info(f"Document embedding for {document_id} completed successfully in {process_time:.2f}s")
        except Exception as e:
            logger.error(f"Error during embedding process for document {document_id}: {e!s}")
            raise RuntimeError(f"Embedding process failed for document {document_id}") from e

    except Exception as e:
        # Log with context information for diagnostics
        logger.exception(f"Error processing document for embedding: {e!s}")
        raise
