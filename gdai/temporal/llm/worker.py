import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from .activity import LLMActivity
from .workflow import LLMWorkflow


async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="llm-queue",
        workflows=[LLMWorkflow],
        activities=[LLMActivity().chat],
    )
    print("Worker started.")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
