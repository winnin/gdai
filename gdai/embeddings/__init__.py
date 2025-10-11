from gdai.commons.settings import get_settings
from gdai.embeddings.cohere_embedding import CohereEmbeddingModel

from .base_embedding import EmbeddingModel  # noqa: F401


class EmbeddingFactory:
    @staticmethod
    async def get_embedding():
        settings = get_settings()
        embedding_config = settings.embedding
        model_name = embedding_config.model
        api_key = embedding_config.api_key or ""
        if model_name == "cohere/embed-v4.0":
            return await CohereEmbeddingModel.create(api_key)
        else:
            raise ValueError(f"Unsupported embedding model: {model_name}")
