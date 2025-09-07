from datetime import timedelta

from temporalio import workflow

from gdai.temporal.llm.schema import PromptInput


@workflow.defn
class LLMWorkflow:
    @workflow.run
    async def run(self, prompt_input: PromptInput) -> str:
        result = await workflow.execute_activity("chat", prompt_input, schedule_to_close_timeout=timedelta(seconds=60))
        return result
