from __future__ import annotations

from abc import ABC, abstractmethod


class LLMModel(ABC):
    """A base class for LLM (Large Language Model) models.

    Attributes:
        model_name (str): The name of the LLM model.
    """

    def __init__(self, model_name: str):
        """Initialize the LLM model.

        Args:
            model_name (str): The name of the LLM model.
        """
        self.model_name = model_name

    @abstractmethod
    async def call_llm(self, prompt: str) -> str:
        """Generate text based on a given prompt.

        Args:
            prompt (str): The input prompt for text generation.

        Returns:
            str: The generated text.
        """
        pass

    def __str__(self) -> str:
        """Return a string representation of the LLM model.

        Returns:
            str: The name of the LLM model.
        """
        return self.model_name
