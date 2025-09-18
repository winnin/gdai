from temporalio import activity

from gdai.llms import LLMFactory

from .schema import PromptInput


class LLMActivity:
    __LLM_MODEL = None

    async def get_llm_model(self):
        if LLMActivity.__LLM_MODEL is None:
            LLMActivity.__LLM_MODEL = await LLMFactory.get_llm()
        return LLMActivity.__LLM_MODEL

    def __format_output(self, user_message, system_message) -> str:
        return f"User: {user_message}\nSystem: {system_message}"

    @activity.defn
    async def chat(self, input: PromptInput) -> str:
        user_message = input.user_prompt
        system_message = input.system_prompt
        prompt = self.__format_output(user_message, system_message)
        llm_model = await self.get_llm_model()
        response = await llm_model.call_llm(prompt)
        return response
