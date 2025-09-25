import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from gdai.commons.logger import logger

from .activity import embedding_texts
from .workflow import TextEmbeddingWorkflow


async def main():
    try:
        logger.info("Initializing TextEmbeddingWorkflow worker...")
        client = await Client.connect("localhost:7233")
        logger.info("Successfully connected to Temporal server at localhost:7233")

        worker = Worker(
            client,
            task_queue="embedding-text-queue",
            workflows=[TextEmbeddingWorkflow],
            activities=[embedding_texts],
            max_concurrent_activities=1,  # limit to 1 activity at a time
            max_concurrent_workflow_tasks=1,  # limit to 1 workflow at a time
            max_task_queue_activities_per_second=1.6,  # limit to 1.6 activities per second 100/60
        )
        logger.info("Worker TextEmbeddingWorkflow started using queue embedding-text-queue")
        logger.info("Starting worker execution...")
        await worker.run()

    except Exception as e:
        logger.error(f"Failed to start TextEmbeddingWorkflow worker: {e}")
        logger.exception("Worker startup error details")
        raise


if __name__ == "__main__":
    logger.info("Starting TextEmbeddingWorkflow worker application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Worker application failed: {e}")
        logger.exception("Application error details")
        raise
