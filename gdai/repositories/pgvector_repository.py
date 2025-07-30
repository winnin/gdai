"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

from sqlalchemy import delete, select, update

from gdai.config.sqlalchemy import SessionLocal
from gdai.mappers import ChunkMapper, DocumentMapper
from gdai.repositories.base_repository import BaseRepository
from gdai.repositories.models import ChunkModel, DocumentModel
from gdai.schemas import Document


class PGVectorRepository(BaseRepository):
    """Repository for managing documents and chunks in PostgreSQL with pgvector."""

    def __init__(self):
        super().__init__()

    async def get_document(self, tenant_id: str, document_id: str) -> Document:
        """Get a document by tenant ID and document ID."""

        async with SessionLocal() as session:
            query = select(DocumentModel).where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document_id)
            result = await session.execute(query)
            document_model = result.scalars().first()
            if not document_model:
                raise ValueError(f"Document with ID {document_id} not found for tenant {tenant_id}.")
            document = DocumentMapper.to_schema(document_model)
            return document

    async def get_document_chunks(self, tenant_id: str, document_id: str) -> list[Document]:
        """Get all chunks for a specific document."""
        async with SessionLocal() as session:
            query = select(ChunkModel).where(ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == document_id)
            result = await session.execute(query)
            chunks_model = result.scalars().all()
            if not chunks_model:
                raise ValueError(f"No chunks found for document ID {document_id} in tenant {tenant_id}.")
            chunks = [ChunkMapper.to_schema(chunk) for chunk in chunks_model]
            return chunks

    async def update_document(self, document: Document) -> None:
        """Update a document in the database.

        Args:
            document: The Document model to update

        Returns:
            Document: The updated document
        """
        async with SessionLocal() as session:
            # Convert the schema document to a database model
            query = (
                update(DocumentModel)
                .where(DocumentModel.tenant_id == document.tenant_id, DocumentModel.id == document.id)
                .values(name=document.name, status=document.status, type=document.type, updated_at=document.updated_at)
            )
            await session.execute(query)

            query = select(DocumentModel).where(
                DocumentModel.tenant_id == document.tenant_id, DocumentModel.id == document.id
            )
            result = await session.execute(query)
            document_model = result.scalars().first()

            # Convert back to schema document
            return DocumentMapper.to_schema(document_model)

    async def update_chunks(self, chunks: list[Document]) -> None:
        """Update chunks in the database.

        Args:
            chunks: A list of Document models to update


        """
        async with SessionLocal() as session:
            for chunk in chunks:
                stmt = update(ChunkModel).where(ChunkModel.id == chunk.id).values(chunk.model_dump())
                await session.execute(stmt)

            # async session has no batch update
            await session.commit()

    async def insert_document_and_chunks(self, document: Document) -> None:
        """Insert a document and its associated chunks into the database.

        Args:
            document: The Document model to insert

        Returns:
            Document: The inserted document with updated IDs
        """
        async with SessionLocal() as session:
            # Convert the schema document to a database model

            document_model = DocumentMapper.to_model(document)
            session.add(document_model)
            await session.flush()

            # Now chunks can reference the document ID
            chunks_model = []
            for chunk in document.chunks:
                chunk_model = ChunkMapper.to_model(chunk)
                chunk_model.document_id = document_model.id  # Set relationship explicitly
                chunks_model.append(chunk_model)

            session.add_all(chunks_model)
            await session.commit()

    async def delete_document_and_chunks(self, document_id: str) -> None:
        """Delete a document and its associated chunks from the database.

        Args:
            document_id: The ID of the document to delete

        """
        async with SessionLocal() as session:
            await session.execute(delete(ChunkModel).where(ChunkModel.document_id == document_id))
            await session.execute(delete(DocumentModel).where(DocumentModel.id == document_id))
            await session.commit()

    async def remove_tenant_content(self, tenant_id: str) -> None:
        """Remove all content for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose content should be removed


        """

        async with SessionLocal() as session:
            await session.execute(delete(DocumentModel).where(DocumentModel.tenant_id == tenant_id))
            await session.commit()
