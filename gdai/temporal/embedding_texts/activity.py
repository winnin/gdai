from temporalio import activity

from gdai.commons.config import Config
from gdai.embeddings import EmbeddingFactory


@activity.defn
async def embedding_texts(text_to_embedding: dict[str, str]) -> dict[str, list[float]]:
    embedding_model = await EmbeddingFactory.get_embedding()
    batch_size = Config.embedding.BATCH_SIZE
    if len(text_to_embedding) > batch_size:
        raise ValueError(f"Number of texts to embed {len(text_to_embedding)} exceeds the max batch size {batch_size}")
    max_text_size = Config.embedding.MAX_TEXT_SIZE
    texts = [text[:max_text_size] for text in text_to_embedding.values()]
    embeddings = await embedding_model.generate_texts_embeddings(texts)
    result = {}
    for id, embedding in zip(text_to_embedding.keys(), embeddings, strict=False):
        result[id] = embedding
    return result
