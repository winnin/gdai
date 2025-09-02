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
        max_concurrent_activities=1,  # limit to 1 activity at a time
        max_concurrent_workflow_tasks=1,  # limit to 1 workflow at a time
        max_task_queue_activities_per_second=1.6,  # limit to 1.6 activities per second 100/60
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
