import asyncio
import uuid

from temporalio.client import Client

from gdai.temporal.search_on_documents.schema import PromptInput


async def main() -> None:
    client = await Client.connect("localhost:7233")
    input = PromptInput(
        user_prompt="What is the best marketing strategy for a new digital product launch?",
        system_prompt="You are a helpful marketing assistent.",
    )

    result = await client.execute_workflow("LLMWorkflow", input, id=f"test_llm_{uuid.uuid4()}", task_queue="llm-queue")
    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
