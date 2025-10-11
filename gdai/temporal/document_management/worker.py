"""Worker for document management workflows."""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from gdai.commons.logger import logger

from .activity import (
    delete_document,
    get_document,
    get_document_chunks,
    get_document_status,
    list_documents,
)
from .workflow import (
    DeleteDocumentWorkflow,
    GetDocumentChunksWorkflow,
    GetDocumentStatusWorkflow,
    GetDocumentWorkflow,
    ListDocumentsWorkflow,
)


async def main():
    """Start the document management worker."""
    try:
        logger.info("Initializing Document Management worker...")
        client = await Client.connect("localhost:7233")
        logger.info("Successfully connected to Temporal server at localhost:7233")

        worker = Worker(
            client,
            task_queue="document-management-queue",
            workflows=[
                ListDocumentsWorkflow,
                GetDocumentWorkflow,
                DeleteDocumentWorkflow,
                GetDocumentChunksWorkflow,
                GetDocumentStatusWorkflow,
            ],
            activities=[
                list_documents,
                get_document,
                delete_document,
                get_document_chunks,
                get_document_status,
            ],
        )
        logger.info("Worker Document Management started using queue document-management-queue")
        logger.info("Starting worker execution...")
        await worker.run()
    except Exception as e:
        logger.error(f"Failed to start Document Management worker: {e}")
        logger.exception("Worker startup error details")
        raise


if __name__ == "__main__":
    logger.info("Starting Document Management worker application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Worker application failed: {e}")
        logger.exception("Application error details")
        raise
