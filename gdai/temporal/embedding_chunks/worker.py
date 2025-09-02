import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from gdai.temporal.embedding_chunks.activity import create_chunkfile_with_embeddings, get_chunks_to_embedding
from gdai.temporal.embedding_chunks.workflow import ChunkEmbeddingWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="embedding-chunks-queue",
        workflows=[ChunkEmbeddingWorkflow],
        activities=[get_chunks_to_embedding, create_chunkfile_with_embeddings],
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
