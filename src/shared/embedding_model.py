from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod

import cohere

from src.shared.conf import Config


class EmbeddingModel(ABC):
    """
    A base class for embedding models.

    Attributes:
        model_name (str): The name of the embedding model.
    """

    def __init__(self, model_name: str):
        """
        Initialize the embedding model.

        Args:
            model_name (str): The name of the embedding model.
        """
        self.model_name = model_name

    @abstractmethod
    async def generate_texts_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts (list[str]): A list of input texts.

        Returns:
            list[list[float]]: A list of embedding vectors for the input texts.
        """
        pass

    def __str__(self) -> str:
        """
        Return a string representation of the embedding model.

        Returns:
            str: The name of the embedding model.
        """
        return self.model_name


class CohereEmbeddingModel(EmbeddingModel):
    """
    A specific implementation of the EmbeddingModel that uses the Cohere API.

    Attributes:
        model (str): The name of the Cohere embedding model.
        api_key (str): The API key for the Cohere service.
        cohere (cohere.Client): The Cohere client instance.
        SEARCH_DOCUMENT_TYPE (str): The input type for the embedding model.
    """

    def __init__(self):
        """
        Initialize the Cohere embedding model.
        """
        self.model = "embed-v4.0"
        model_name = f"cohere/{self.model}"
        super().__init__(model_name)
        self.cohere = None
        self.SEARCH_DOCUMENT_TYPE = "search_query"

    @staticmethod
    async def create(api_key: str) -> CohereEmbeddingModel:
        """
        Create a CohereEmbeddingModel instance with the provided API key.

        Args:
            api_key (str): The API key for Cohere.

        Returns:
            CohereEmbeddingModel: The created embedding model instance.
        """
        embedding_model = CohereEmbeddingModel()
        embedding_model.api_key = api_key
        embedding_model.cohere = cohere.AsyncClient(api_key=api_key)
        return embedding_model

    async def generate_texts_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts using the Cohere API.

        Args:
            texts (list[str]): A list of input texts. The maximum number of texts is 96

        Returns:
            list[list[float]]: A list of embedding vectors for the input texts.

        Raises:
            Exception: If the API call fails.
        """
        if not texts:
            raise ValueError("The list of texts cannot be empty.")
        if any(not text.strip() for text in texts):
            raise ValueError("The texts cannot be empty strings.")
        if len(texts) > 96:
            raise ValueError("The maximum number of texts is 96.")
        try:
            res = await self.cohere.embed(
                texts=texts,
                model=self.model,
                input_type=self.SEARCH_DOCUMENT_TYPE,
                embedding_types=["float"],
            )
            await asyncio.sleep(3)  # Small delay between batches
            return res.embeddings.float_
        except Exception as e:
            raise Exception(f"Failed to generate embeddings for texts: {e}") from e


class EmbeddingModelFactory:
    """
    A factory class to create instances of embedding models.
    """

    @staticmethod
    async def create() -> EmbeddingModel:
        """
        Create an instance of the specified embedding model.

        Returns:
            EmbeddingModel: An instance of the specified embedding model.
        """
        if Config.ai.EMBEDDING_MODEL == "cohere/embed-v4.0":
            return await CohereEmbeddingModel.create(Config.ai.EMBEDDING_MODEL_API_KEY)
        else:
            raise ValueError(
                f"Unsupported embedding model: {Config.ai.EMBEDDING_MODEL}"
            )
