import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from gdai.commons.logger import logger
from gdai.temporal.embedding_chunks.activity import create_chunkfile_with_embeddings, get_chunks_to_embedding
from gdai.temporal.embedding_chunks.workflow import ChunkEmbeddingWorkflow


async def main():
    try:
        logger.info("Initializing ChunkEmbeddingWorkflow worker...")
        client = await Client.connect("localhost:7233")
        logger.info("Successfully connected to Temporal server at localhost:7233")

        worker = Worker(
            client,
            task_queue="embedding-chunks-queue",
            workflows=[ChunkEmbeddingWorkflow],
            activities=[get_chunks_to_embedding, create_chunkfile_with_embeddings],
        )

        logger.info("Worker ChunkEmbeddingWorkflow started using queue embedding-chunks-queue")
        logger.info("Starting worker execution...")
        await worker.run()

    except Exception as e:
        logger.error(f"Failed to start ChunkEmbeddingWorkflow worker: {e}")
        logger.exception("Worker startup error details")
        raise


if __name__ == "__main__":
    logger.info("Starting ChunkEmbeddingWorkflow worker application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Worker application failed: {e}")
        logger.exception("Application error details")
        raise
