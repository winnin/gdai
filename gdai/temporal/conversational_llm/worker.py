import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from gdai.commons.logger import logger

from .activity import LLMActivity
from .workflow import LLMWorkflow


async def main():
    try:
        logger.info("Initializing LLMWorkflow worker...")
        client = await Client.connect("localhost:7233")
        logger.info("Successfully connected to Temporal server at localhost:7233")

        worker = Worker(
            client,
            task_queue="llm-queue",
            workflows=[LLMWorkflow],
            activities=[LLMActivity().chat],
        )

        logger.info("Worker LLMWorkflow started using queue llm-queue")
        logger.info("Starting worker execution...")
        await worker.run()

    except Exception as e:
        logger.error(f"Failed to start LLMWorkflow worker: {e}")
        logger.exception("Worker startup error details")
        raise


if __name__ == "__main__":
    logger.info("Starting LLMWorkflow worker application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Worker application failed: {e}")
        logger.exception("Application error details")
        raise
