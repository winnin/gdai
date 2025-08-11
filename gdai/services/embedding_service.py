"""Module for processing documents through an embedding pipeline."""

from __future__ import annotations

import asyncio

from gdai.commons.enums import DocumentStatusEnum
from gdai.config.logger import logger
from gdai.config.settings import Config
from gdai.embeddings.base_embedding import EmbeddingModel
from gdai.repositories.base_repository import BaseRepository


class EmbeddingDocumentChunksService:
    """Service for embedding document chunks."""

    def __init__(self, embedding_model: EmbeddingModel, repository: BaseRepository):
        """Initialize with embedding model and repository."""
        self.embedding_model = embedding_model
        self.repository = repository
        self.batch_size = Config.embedding.BATCH_SIZE
        self.embedding_chunk_size = Config.embedding.CHUNK_SIZE

    async def embed_document_chunks(self, tenant_id: str, document_id: str) -> None:
        """Embed chunks of a specific document."""
        try:
            chunks = await self.repository.get_chunks(tenant_id, document_id)
            chunks = [chunk for chunk in chunks if chunk.embedding is None]  # to embed only chunks without embedding

            if not chunks:
                logger.info(f"No chunks to embed for document id: {document_id}")
                document = await self.repository.get_document(tenant_id, document_id)
                document.status = DocumentStatusEnum.processed
                logger.info(f"Finishing embedding for document id:{document.id} - name:{document.name}")
                await self.repository.update_document(tenant_id, document_id)
                return

            for i in range(0, len(chunks), self.batch_size + 1):
                chunk_batch = chunks[i : i + self.batch_size]
                texts = [chunk.chunk[: self.embedding_chunk_size] for chunk in chunk_batch]
                embeddings = await self.embedding_model.generate_texts_embeddings(texts)
                for chunk, embedding in zip(chunk_batch, embeddings, strict=False):
                    chunk.embedding = embedding
                await self.repository.update_chunks(tenant_id, chunk_batch)  # update the embedding for each chunk
                await asyncio.sleep(3)  # rate limit for cohere

        except Exception as e:
            document = await self.repository.get_document(tenant_id, document_id)
            document.retry_embedding += 1
            if document.retry_embedding >= Config.embedding.MAX_RETRIES:
                document.status = DocumentStatusEnum.embedding_failed
            else:
                document.status = DocumentStatusEnum.extracted  # back to extracted to retry embedding

            await self.repository.update_document(tenant_id, document)

            logger.error(f"Failed to embed document chunks from {document_id} {e!s}")
            await asyncio.sleep(60)  # avoid problems with rate limit
