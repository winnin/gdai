"""Module for processing documents through an embedding pipeline."""

from __future__ import annotations

import asyncio

from gdai.config.logger import logger
from gdai.embeddings.base_embedding import EmbeddingModel
from gdai.repositories.base_repository import BaseRepository
from gdai.schemas import Chunk


class EmbeddingBatchService:
    """Service for processing batches of chunks through an embedding pipeline."""

    def __init__(self, embedding_model: EmbeddingModel, repository: BaseRepository):
        """Initialize with embedding model, repository, and chunking parameters."""
        self.embedding_model: EmbeddingModel = embedding_model
        self.repository = repository

    async def embed_chunks(self, tenant_id: str, chunks: list[Chunk]) -> None:
        """Process chunks: load, embed, and store in repository."""

        try:
            texts = [chunk.chunk[:1024] for chunk in chunks]  # TODO: add chunk limit size to config
            embeddings = await self.embedding_model.generate_texts_embeddings(texts)

            for chunk, embedding in zip(chunks, embeddings, strict=False):
                chunk.embedding = embedding
            await self.repository.update_chunks(tenant_id, chunks)  # update the embedding for each chunk
            await asyncio.sleep(3)  # rate limit for cohere
        except Exception as e:
            logger.error(f"Failed to embed chunks: {e!s}")
            await asyncio.sleep(60)  # rate limit for cohere
