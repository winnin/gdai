import asyncio
import traceback
import uuid

from temporalio.client import Client, WorkflowFailureError


async def main() -> None:
    # Create client connected to server at the given address
    client: Client = await Client.connect("localhost:7233")

    input = {
        str(uuid.uuid4()): "This is the first chunk.",
        str(uuid.uuid4()): "This is the second chunk.",
        str(uuid.uuid4()): "This is the third chunk.",
    }

    try:
        result = await client.execute_workflow(
            "TextEmbeddingWorkflow",
            input,
            id=f"test_embedding_text_{uuid.uuid4()}",
            task_queue="embedding-text-queue",
        )

        print(f"Result: {result}")

    except WorkflowFailureError as e:
        print("Got expected exception: ", traceback.format_exc())
        raise e


if __name__ == "__main__":
    asyncio.run(main())
