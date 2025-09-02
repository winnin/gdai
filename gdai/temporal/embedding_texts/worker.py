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
        max_concurrent_activities=1,  # Limita a 1 atividade simultânea
        max_concurrent_workflow_tasks=1,  # Limita a 1 workflow simultâneo
        max_task_queue_activities_per_second=1.6,  # Limita a 1.6 atividades por segundo 100/60
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
