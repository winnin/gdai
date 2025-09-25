from temporalio.client import Client
from temporalio.worker import Worker

from gdai.commons.logger import logger

from .activity import format_answer, generate_prompt_from_template, get_chunks, register_query, save_query_result
from .workflow import DocumentSearchWorkflow


async def main():
    try:
        logger.info("Initializing DocumentSearchWorkflow worker...")
        client = await Client.connect("localhost:7233")
        logger.info("Successfully connected to Temporal server at localhost:7233")

        worker = Worker(
            client,
            task_queue="search-on-documents-queue",
            workflows=[DocumentSearchWorkflow],
            activities=[get_chunks, generate_prompt_from_template, register_query, save_query_result, format_answer],
        )
        logger.info("Worker DocumentSearchWorkflow started using queue search-on-documents-queue")
        logger.info("Starting worker execution...")
        await worker.run()
    except Exception as e:
        logger.error(f"Failed to start DocumentSearchWorkflow worker: {e}")
        logger.exception("Worker startup error details")
        raise


if __name__ == "__main__":
    import asyncio

    logger.info("Starting DocumentSearchWorkflow worker application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Worker application failed: {e}")
        logger.exception("Application error details")
        raise
