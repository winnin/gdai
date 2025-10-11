from gdai.commons.settings import get_settings
from gdai.llms.base_llm import LLMModel
from gdai.llms.openai_llm import OpenAIModel


class LLMFactory:
    @staticmethod
    async def get_llm() -> LLMModel:
        settings = get_settings()
        llm_config = settings.llm
        model_name = llm_config.model
        api_key = llm_config.api_key or ""
        temperature = llm_config.temperature
        max_tokens = llm_config.max_tokens
        if "openai" in model_name:
            openai_model_name = model_name.split("/")[1]
            return await OpenAIModel.create(openai_model_name, api_key, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported LLM model: {model_name}")
