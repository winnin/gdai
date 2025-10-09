import uuid

from temporalio.client import Client

from gdai.temporal.search_on_documents.schema import SearchInput


async def main() -> None:
    client = await Client.connect("localhost:7233")
    input = SearchInput(
        query_id=f"{uuid.uuid4()}",
        query="Quais são os personagens que aparecem em Alice no País das Maravilhas?, responda em portugues",
        tenant_id="tenant_123",
        similarity_threshold=0.10,
        max_num_chunks=30,
        document_ids=[],
    )
    result = await client.execute_workflow(
        "DocumentSearchWorkflow",
        input,
        id=f"test_search_{uuid.uuid4()}",
        task_queue="search-on-documents-queue",
    )
    # Ensure the workflow executes without interactive debugging
    print(f"Result: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
