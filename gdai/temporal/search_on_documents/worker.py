from temporalio.client import Client
from temporalio.worker import Worker

from .activity import generate_prompt_from_template, get_chunks, register_query
from .workflow import DocumentSearchWorkflow


async def main():
    client = await Client.connect("localhost:7233")

    worker = Worker(
        client,
        task_queue="search-on-documents-queue",
        workflows=[DocumentSearchWorkflow],
        activities=[get_chunks, generate_prompt_from_template, register_query],
    )
    print("Worker DocumentSearchWorkflow started using queue search-on-documents-queue.")
    await worker.run()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
