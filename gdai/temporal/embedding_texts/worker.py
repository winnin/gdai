import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activity import embedding_texts
from .workflow import TextEmbeddingWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="embedding-text-queue",
        workflows=[TextEmbeddingWorkflow],
        activities=[embedding_texts],
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
