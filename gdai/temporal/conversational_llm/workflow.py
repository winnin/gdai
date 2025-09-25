from datetime import timedelta

from temporalio import workflow

from .schema import PromptInput


@workflow.defn
class LLMWorkflow:
    @workflow.run
    async def run(self, prompt_input: PromptInput) -> str:
        try:
            workflow.logger.info("Starting LLMWorkflow execution")
            workflow.logger.debug(
                f"""User prompt length: {len(prompt_input.user_prompt)},
                System prompt length: {len(prompt_input.system_prompt)}"""
            )

            workflow.logger.info("Executing chat activity")
            result = await workflow.execute_activity(
                "chat", prompt_input, schedule_to_close_timeout=timedelta(seconds=60)
            )

            workflow.logger.info(f"LLMWorkflow completed successfully, response length: {len(result)}")
            return result

        except Exception as e:
            workflow.logger.error(f"LLMWorkflow failed: {e}")
            raise
