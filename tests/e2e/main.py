import asyncio
import traceback
import uuid

from temporalio.client import Client, WorkflowFailureError

from gdai.temporal.extract_document.schema import DocumentExtracInput
from gdai.temporal.extract_document.workflow import DocumentExtractionWorkflow


async def main() -> None:
    # Create client connected to server at the given address
    client: Client = await Client.connect("localhost:7233")

    input = DocumentExtracInput(
        document_path="/home/fabricio/Desktop/data/senhor_dos_aneis.pdf",
        chunk_strategy="sentence",
        tenant_id="tenant_123",
    )

    try:
        result = await client.execute_workflow(
            DocumentExtractionWorkflow.run,
            input,
            id=f"test_extract_document_{uuid.uuid4()}",
            task_queue="process-document-queue",
        )

        print(f"Result: {result}")

    except WorkflowFailureError as e:
        print("Got expected exception: ", traceback.format_exc())
        raise e


if __name__ == "__main__":
    asyncio.run(main())
