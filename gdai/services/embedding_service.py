"""Module for processing documents through an embedding pipeline."""

from __future__ import annotations

import uuid

from gdai.commons.enums import DocumentStatusEnum
from gdai.embeddings.base_embedding import EmbeddingModel
from gdai.repositories.base_repository import BaseRepository


class EmbeddingDocumentService:
    """Service for processing documents through an embedding pipeline."""

    def __init__(self, embedding_model: EmbeddingModel, repository: BaseRepository, batch_size: int = 64):
        """Initialize with embedding model, repository, and chunking parameters."""
        self.embedding_model: EmbeddingModel = embedding_model
        self.repository = repository
        self.batch_size = batch_size

    async def process_document(self, tenant_id: str, document_id: uuid.UUID) -> None:
        """Process document: load, chunk, embed, and store in repository."""

        try:
            document_id_str = str(document_id)
            # change document status
            document = await self.repository.get_document(tenant_id, document_id_str)
            document.status = DocumentStatusEnum.embedding
            await self.repository.update_document(tenant_id, document)

            # get chunks
            chunks = await self.repository.get_chunks(tenant_id, document_id_str)

            # for each chunk send a embedding request (check implementation in embeddings)
            for i in range(0, len(chunks), self.batch_size):
                batch = chunks[i : i + self.batch_size]
                texts = [chunk.chunk[:1024] for chunk in batch]  # PUT LIMIT ON TEXT LENGTH ON .ENV
                embeddings = await self.embedding_model.generate_texts_embeddings(texts)
                for chunk, embedding in zip(batch, embeddings, strict=False):
                    chunk.embedding = embedding
                await self.repository.update_chunks(tenant_id, chunks)  # update the embedding for each chunk

            # change status of document and chunks
            document.status = DocumentStatusEnum.processed
            await self.repository.update_document(tenant_id, document)
        except Exception as e:
            document.status = DocumentStatusEnum.embedding_failed
            await self.repository.update_document(tenant_id, document)
            raise e
