from __future__ import annotations

from abc import ABC, abstractmethod

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from src.shared.conf import Config


class LLMModel(ABC):
    """
    A base class for LLM (Large Language Model) models.

    Attributes:
        model_name (str): The name of the LLM model.
    """

    def __init__(self, model_name: str):
        """
        Initialize the LLM model.

        Args:
            model_name (str): The name of the LLM model.
        """
        self.model_name = model_name

    @abstractmethod
    async def call_llm_stream(self, prompt: str) -> str:
        """
        Generate text based on a given prompt.

        Args:
            prompt (str): The input prompt for text generation.

        Returns:
            str: The generated text.
        """
        pass

    def __str__(self) -> str:
        """
        Return a string representation of the LLM model.

        Returns:
            str: The name of the LLM model.
        """
        return self.model_name


class OpenAIModel(LLMModel):
    """
    A specific implementation of the LLMModel that uses the OpenAI API.

    Attributes:
        model_name (str): The name of the OpenAI model.
        api_key (str): The API key for the OpenAI service.
    """

    def __init__(
        self, model_name: str, api_key: str, temperature: float, max_tokens: int
    ):
        """
        Initialize the OpenAI model.

        Args:
            model_name (str): The name of the OpenAI model.
        """
        self.llm_model_name = model_name
        self.api_key = api_key
        super().__init__(self.llm_model_name)
        self.llm = ChatOpenAI(
            model_name=self.llm_model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            openai_api_key=self.api_key,
            streaming=True,
        )

    @staticmethod
    async def create(
        model_name: str, api_key: str, temperature: float = 0.7, max_tokens: int = 1000
    ) -> OpenAIModel:
        """
        Create an instance of OpenAIModel with the provided API key.

        Args:
            api_key (str): The API key for the OpenAI service.
            temperature (float): The temperature for text generation.
            max_tokens (int): The maximum number of tokens to generate.

        Returns:
            OpenAIModel: An instance of OpenAIModel.
        """
        model = OpenAIModel(model_name, api_key, temperature, max_tokens)
        return model

    async def call_llm_stream(self, prompt):
        """
        Answer a question using the LLM model with a given query and context.

        Args:
            query_prompt (str): The input query prompt.
            rag_context (list): A list of context strings to provide additional information.

        Returns:
            str: The generated answer from the LLM model.
        """

        messages = [HumanMessage(content=prompt)]

        # Usa o método .stream() para receber partes do texto incrementalmente
        for chunk in self.llm.stream(messages):
            # Cada chunk é uma mensagem parcial (como delta no ChatCompletion)
            yield chunk.content


class LLMModelFactory:
    """
    A factory class for creating instances of LLMModel based on the configuration.
    """

    @staticmethod
    async def create() -> LLMModel:
        """
        Create an instance of LLMModel based on the configuration.

        Returns:
            LLMModel: An instance of OpenAIModel.
        """
        model_name = Config.ai.LLM_MODEL
        api_key = Config.ai.LLM_MODEL_API_KEY
        temperature = Config.ai.LLM_TEMPERATURE
        max_tokens = Config.ai.LLM_MAX_TOKENS
        if "openai" in model_name:
            openai_model_name = model_name.split("/")[1]
            return await OpenAIModel.create(
                openai_model_name, api_key, temperature, max_tokens
            )

        raise ValueError("Invalid SEARCH_LLM_MODEL configuration")
