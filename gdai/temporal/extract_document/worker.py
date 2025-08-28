import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activity import (
    chunk_texts,
    extract,
    store,
    validate,
)
from .workflow import DocumentExtractionWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="process-document-queue",
        workflows=[DocumentExtractionWorkflow],
        activities=[
            validate,
            extract,
            chunk_texts,
            store,
        ],
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
