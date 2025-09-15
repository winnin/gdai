from gdai.commons.config import Config
from gdai.llms.base_llm import LLMModel
from gdai.llms.openai_llm import OpenAIModel


class LLMFactory:
    @staticmethod
    async def get_llm() -> LLMModel:
        model_name = Config.llm.LLM_MODEL
        api_key = Config.llm.LLM_MODEL_API_KEY or ""
        temperature = Config.llm.LLM_TEMPERATURE
        max_tokens = Config.llm.LLM_MAX_TOKENS
        if "openai" in model_name:
            openai_model_name = model_name.split("/")[1]
            return await OpenAIModel.create(openai_model_name, api_key, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM model: {model_name}")
