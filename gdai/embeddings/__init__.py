from gdai.config.settings import Config
from gdai.embeddings.cohere_embedding import CohereEmbeddingModel


class EmbeddingFactory:
    @staticmethod
    async def get_embedding():
        model_name = Config.ai.EMBEDDING_MODEL
        api_key = Config.ai.EMBEDDING_MODEL_API_KEY or ""
        if model_name == "cohere/embed-v4.0":
            return await CohereEmbeddingModel.create(api_key)
        else:
            raise ValueError(f"Unsupported embedding model: {model_name}")
