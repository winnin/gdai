import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from gdai.commons.logger import logger

from .activity import (
    chunk_texts,
    extract,
    remove_temp_files,
    store_embedded_chunks,
    validate,
)
from .workflow import DocumentExtractionWorkflow


async def main():
    try:
        logger.info("Initializing DocumentExtractionWorkflow worker...")
        client = await Client.connect("localhost:7233")
        logger.info("Successfully connected to Temporal server at localhost:7233")

        worker = Worker(
            client,
            task_queue="process-document-queue",
            workflows=[DocumentExtractionWorkflow],
            activities=[
                validate,
                extract,
                chunk_texts,
                store_embedded_chunks,
                remove_temp_files,
            ],
        )
        logger.info("Worker DocumentExtractionWorkflow started using queue process-document-queue")
        logger.info("Starting worker execution...")
        await worker.run()
    except Exception as e:
        logger.error(f"Failed to start DocumentExtractionWorkflow worker: {e}")
        logger.exception("Worker startup error details")
        raise


if __name__ == "__main__":
    logger.info("Starting DocumentExtractionWorkflow worker application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Worker application failed: {e}")
        logger.exception("Application error details")
        raise
