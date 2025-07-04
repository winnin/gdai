import asyncio
import json
import os
from time import time

import psutil

from src.config.broker import dramatiq
from src.config.logger import logger
from src.config.settings import Config
from src.embeddings import EmbeddingFactory
from src.repositories import RepositoryFactory
from src.services.embedding import EmbeddingDocumentService

try:
    document_repository = RepositoryFactory.get_repository().document
    embedding_model = asyncio.run(EmbeddingFactory.get_embedding())
    embedding_service = EmbeddingDocumentService(
        embedding_model=embedding_model,
        chunk_size=Config.embedding.CHUNK_SIZE,
        chunk_overlap=Config.embedding.CHUNK_OVERLAP,
        document_repository=document_repository,
    )
    logger.info(f"Embedding service initialized successfully with model: {embedding_model !s}")
except Exception as e:
    logger.critical(f"Failed to initialize embedding components: {e!s}")
    raise RuntimeError("Embedding service initialization failed") from e


@dramatiq.actor(
    queue_name=Config.embedding.QUEUE,
    max_retries=Config.embedding.MAX_RETRIES,
    min_backoff=Config.embedding.RETRY_DELAY,
)
def embedding_document(message_data: dict):
    start_time = time()
    try:
        # Validate that the incoming message is a dictionary
        # This ensures we can access expected fields safely
        if not isinstance(message_data, dict):
            logger.error(f"Invalid message data type: {type(message_data)}")
            raise TypeError("message_data must be a dictionary")

        document_full_path = message_data.get("document_path")
        if not document_full_path:
            logger.error("Missing document_path in message data")
            raise ValueError("document_path is required in message data")

        logger.info(f"Received document for embedding: {document_full_path}")

        if not os.path.exists(document_full_path):
            logger.error(f"Document file {document_full_path} does not exist.")

        # Validate that the document file exists on disk
        try:
            with open(document_full_path, encoding="utf-8") as f:
                document_content = json.load(f)
            if not isinstance(document_content, dict):
                logger.error("Document content is not a valid JSON object")
                raise ValueError("Document content must be a valid JSON object")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse document JSON: {e!s}")
            raise ValueError(f"Invalid JSON format in document: {e!s}")

        # Embedding can be memory-intensive, so we verify we have enough resources
        mem = psutil.virtual_memory()
        if mem.percent > Config.embedding.MAX_MEMORY_USAGE_PERCENT:
            logger.error(f"Insufficient memory to process embedding (Usage: {mem.percent}%)")
            raise RuntimeError(f"System memory usage too high ({mem.percent}%) for safe embedding processing")
        try:
            logger.info(f"Beginning embedding for document {document_full_path}")
            asyncio.run(embedding_service.process_document(document_full_path))
            process_time = time() - start_time
            logger.info(f"Document embedding for {document_full_path} completed successfully in {process_time:.2f}s")
        except Exception as e:
            logger.error(f"Error during embedding process for document {document_full_path}: {e!s}")
            raise RuntimeError(f"Embedding process failed for document {document_full_path}") from e

    except Exception as e:
        # Log with context information for diagnostics
        logger.exception(f"Error processing document for embedding: {e!s}")
        raise
