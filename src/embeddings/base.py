from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingModel(ABC):
    """A base class for embedding models.

    Attributes:
        model_name (str): The name of the embedding model.
    """

    def __init__(self, model_name: str):
        """Initialize the embedding model.

        Args:
            model_name (str): The name of the embedding model.
        """
        self.model_name = model_name

    @abstractmethod
    async def generate_texts_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts (list[str]): A list of input texts.

        Returns:
            list[list[float]]: A list of embedding vectors for the input texts.
        """
        pass

    def __str__(self) -> str:
        """Return a string representation of the embedding model.

        Returns:
            str: The name of the embedding model.
        """
        return self.model_name
