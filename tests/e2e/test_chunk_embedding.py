import asyncio
import traceback
import uuid

from temporalio.client import Client, WorkflowFailureError


async def main() -> None:
    # Create client connected to server at the given address
    client: Client = await Client.connect("localhost:7233")

    try:
        result = await client.execute_workflow(
            "ChunkEmbeddingWorkflow",
            "/home/fabricio/projects/g-dai/DOC_FOLDER/c2e96e94-3ba4-4213-98cc-cce949fe98c8_chunks_0.json",
            id=f"test_embedding_chunk_{uuid.uuid4()}",
            task_queue="embedding-chunks-queue",
        )

        print(f"Result: {result}")

    except WorkflowFailureError as e:
        print("Got expected exception: ", traceback.format_exc())
        raise e


if __name__ == "__main__":
    asyncio.run(main())
