from temporalio import activity

from gdai.commons.logger import logger
from gdai.services.llms import LLMFactory

from .schema import PromptInput


class LLMActivity:
    __LLM_MODEL = None

    async def get_llm_model(self):
        if LLMActivity.__LLM_MODEL is None:
            logger.info("Initializing LLM model for conversational activity")
            LLMActivity.__LLM_MODEL = await LLMFactory.get_llm()
            logger.info(f"LLM model initialized successfully: {LLMActivity.__LLM_MODEL}")
        return LLMActivity.__LLM_MODEL

    def __format_output(self, user_message, system_message) -> str:
        return f"User: {user_message}\nSystem: {system_message}"

    @activity.defn
    async def chat(self, input: PromptInput) -> str:
        try:
            logger.info("Starting chat activity")
            logger.debug(
                f"User prompt length: {len(input.user_prompt)}, System prompt length: {len(input.system_prompt)}"
            )

            user_message = input.user_prompt
            system_message = input.system_prompt
            prompt = self.__format_output(user_message, system_message)

            logger.debug(f"Formatted prompt length: {len(prompt)}")

            llm_model = await self.get_llm_model()

            logger.info("Calling LLM model for response generation")
            response = await llm_model.call_llm(prompt)

            logger.info(f"LLM response generated successfully, length: {len(response)}")
            logger.debug(f"Response preview: {response[:100]}...")

            return response

        except Exception as e:
            logger.error(f"Error in chat activity: {e}")
            raise e
