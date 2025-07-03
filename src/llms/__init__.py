from src.config.settings import Config
from src.llms.base import LLMModel
from src.llms.openai import OpenAIModel


class LLMFactory:
    @staticmethod
    async def get_llm() -> LLMModel:
        model_name = Config.ai.LLM_MODEL
        api_key = Config.ai.LLM_MODEL_API_KEY or ""
        temperature = Config.ai.LLM_TEMPERATURE
        max_tokens = Config.ai.LLM_MAX_TOKENS
        if "openai" in model_name:
            openai_model_name = model_name.split("/")[1]
            return await OpenAIModel.create(openai_model_name, api_key, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM model: {model_name}")
