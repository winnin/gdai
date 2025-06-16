from __future__ import annotations

import asyncio
import json
import os
from time import time

import psutil

from src.actor.embedding.repository import DocumentRepository
from src.actor.embedding.service import EmbeddingDocumentService
from src.shared.broker import dramatiq  # with configured broked
from src.shared.conf import Config
from src.shared.embedding_model import EmbeddingModelFactory
from src.shared.logger import logger

try:
    document_repository = DocumentRepository()
    embedding_model = asyncio.run(EmbeddingModelFactory.create())
    embedding_service = EmbeddingDocumentService(
        embedding_model=embedding_model,
        chunk_size=Config.embedding.CHUNK_SIZE,
        chunk_overlap=Config.embedding.CHUNK_OVERLAP,
        document_repository=document_repository,
    )
    logger.info(
        f"Embedding service initialized successfully with model: {embedding_model !s}"
    )
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

        document_name = message_data.get("document_name")
        if not document_name:
            logger.error("Missing document_name in message data")
            raise ValueError("document_name is required in message data")

        logger.info(f"Received document for embedding: {document_name}")

        # Validate that the document name is provided
        document_full_path = os.path.join(
            Config.embedding.FOLDER_EXTRACTED_DOC_PATH, document_name
        )
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
            logger.error(
                f"Insufficient memory to process embedding (Usage: {mem.percent}%)"
            )
            raise RuntimeError(
                f"System memory usage too high ({mem.percent}%) for safe embedding processing"
            )
        try:
            logger.info(
                f"Beginning embedding for document {document_name} at {document_full_path}"
            )
            asyncio.run(embedding_service.process_document(document_full_path))
            process_time = time() - start_time
            logger.info(
                f"Document embedding for {document_name} completed successfully in {process_time:.2f}s"
            )
        except Exception as e:
            logger.error(
                f"Error during embedding process for document {document_name}: {e!s}"
            )
            raise RuntimeError(
                f"Embedding process failed for document {document_name}"
            ) from e

    except Exception as e:
        # Log with context information for diagnostics
        logger.exception(f"Error processing document for embedding: {e!s}")
        raise
