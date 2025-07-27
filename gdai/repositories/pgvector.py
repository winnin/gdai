"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

from sqlalchemy import delete

from gdai.config.sqlalchemy import SessionLocal
from gdai.mappers import ChunkMapper, DocumentMapper
from gdai.repositories.base import BaseRepository
from gdai.repositories.models import ChunkModel, DocumentModel
from gdai.schemas import Document


class PGVectorRepository(BaseRepository):
    """Repository for managing documents and chunks in PostgreSQL with pgvector."""

    def __init__(self):
        super().__init__()

    async def get_document(self, tenant_id: str, document_id: str) -> Document:
        """Get a document by tenant ID and document ID."""
        async with SessionLocal() as session:
            document_model = (
                session.query(DocumentModel)
                .filter(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document_id)
                .first()
            )
            if not document_model:
                raise ValueError(f"Document with ID {document_id} not found for tenant {tenant_id}.")
            document = DocumentMapper.to_schema(document_model)
            return document

    async def get_document_chunks(self, tenant_id: str, document_id: str) -> list[Document]:
        """Get all chunks for a specific document."""
        async with SessionLocal() as session:
            chunks_model = (
                session.query(ChunkModel)
                .filter(ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == document_id)
                .all()
            )
            chunks = [ChunkMapper.to_schema(chunk) for chunk in chunks_model]
            return chunks

    async def update_document(self, document: Document) -> Document:
        """Update a document in the database.

        Args:
            document: The Document model to update

        Returns:
            Document: The updated document
        """
        async with SessionLocal() as session:
            # Convert the schema document to a database model
            document_model = DocumentMapper.to_model(document)

            # Update the document in the database
            session.merge(document_model)
            await session.commit()
            await session.refresh(document_model)

            # Convert back to schema document
            return DocumentMapper.to_schema(document_model)
        # arrumar monte de coisa

    async def update_chunks(self, chunks: list[Document]) -> list[Document]:
        """Update chunks in the database.

        Args:
            chunks: A list of Document models to update

        Returns:
            list[Document]: The updated chunks
        """
        async with SessionLocal() as session:
            chunk_models = [ChunkMapper.to_model(chunk) for chunk in chunks]
            session.bulk_update_mappings(ChunkModel, [chunk.dict() for chunk in chunk_models])
            await session.commit()

            # Refresh and convert back to schema
            updated_chunks = []
            for chunk_model in chunk_models:
                await session.refresh(chunk_model)
                updated_chunks.append(ChunkMapper.to_schema(chunk_model))

            return updated_chunks

    async def insert_document_and_chunks(self, document: Document) -> Document:
        """Insert a document and its associated chunks into the database.

        Args:
            document: The Document model to insert

        Returns:
            Document: The inserted document with updated IDs
        """
        async with SessionLocal() as session:
            # Convert the schema document to a database model

            document_model = DocumentMapper.to_model(document)
            chunks_model = [ChunkMapper.to_model(chunk) for chunk in document.chunks]

            # Add to session and commit
            session.add_all([document_model] + chunks_model)
            await session.commit()
            await session.refresh(document_model)
            # Replace refresh_all with individual refresh calls
            for chunk in chunks_model:
                await session.refresh(chunk)

            # Convert back to schema document
            doc = DocumentMapper.to_schema(document_model)
            doc.chunks = [ChunkMapper.to_schema(chunk) for chunk in chunks_model]

            return doc

    async def delete_document_and_chunks(self, document_id: str) -> bool:
        """Delete a document and its associated chunks from the database.

        Args:
            document_id: The ID of the document to delete

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        async with SessionLocal() as session:
            await session.execute(delete(ChunkModel).where(ChunkModel.document_id == document_id))
            await session.execute(delete(DocumentModel).where(DocumentModel.id == document_id))
            await session.commit()

        return True

    async def remove_tenant_content(self, tenant_id: str) -> bool:
        """Remove all content for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose content should be removed

        Returns:
            bool: True if the operation was successful, False otherwise
        """

        async with SessionLocal() as session:
            await session.execute(delete(DocumentModel).where(DocumentModel.tenant_id == tenant_id))
            await session.commit()

        return True
