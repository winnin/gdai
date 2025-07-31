"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

from sqlalchemy import delete, insert, select, update

from gdai.config.sqlalchemy import SessionLocal
from gdai.mappers import ChunkMapper, DocumentMapper
from gdai.repositories.base_repository import BaseRepository
from gdai.repositories.models import ChunkModel, DocumentModel
from gdai.schemas import Chunk, Document


class PGVectorRepository(BaseRepository):
    """Repository for managing documents and chunks in PostgreSQL with pgvector."""

    def __init__(self):
        super().__init__()

    async def get_document(self, tenant_id: str, document_id: str) -> Document:
        """Get a document by tenant ID and document ID."""

        async with SessionLocal() as session:
            try:
                query = select(DocumentModel).where(
                    DocumentModel.tenant_id == tenant_id, DocumentModel.id == document_id
                )
                result = await session.execute(query)
                document_model = result.scalars().first()
                if not document_model:
                    raise ValueError(f"Document with ID {document_id} not found for tenant {tenant_id}.")
            except Exception as e:
                raise ValueError(f"Failed to retrieve document: {e!s}")

            document = DocumentMapper.to_schema(document_model)
            return document

    async def get_document_chunks(self, tenant_id: str, document_id: str) -> list[Chunk]:
        """Get all chunks for a specific document."""
        async with SessionLocal() as session:
            try:
                query = select(ChunkModel).where(
                    ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == document_id
                )
                result = await session.execute(query)
                chunks_model = result.scalars().all()
                if not chunks_model:
                    raise ValueError(f"No chunks found for document ID {document_id} in tenant {tenant_id}.")
                chunks = [ChunkMapper.to_schema(chunk) for chunk in chunks_model]
                return chunks
            except Exception as e:
                raise ValueError(f"Failed to retrieve chunks: {e!s}")

    async def update_document(self, document: Document) -> None:
        """Update a document in the database.

        Args:
            document: The Document model to update

        Returns:
            Document: The updated document
        """
        async with SessionLocal() as session:
            try:
                # Convert the schema document to a database model
                stmt = (
                    update(DocumentModel)
                    .where(DocumentModel.tenant_id == document.tenant_id, DocumentModel.id == document.id)
                    .values(
                        name=document.name, status=document.status, type=document.type, updated_at=document.updated_at
                    )
                )
                await session.execute(stmt)

                document = await self.get_document(tenant_id=document.tenant_id, document_id=document.id)

                return document
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to update document: {e!s}")

    async def update_chunks(self, chunks: list[Document]) -> None:
        """Update chunks in the database.
        Args:
            chunks: A list of Document models to update
        """
        async with SessionLocal() as session:
            try:
                for chunk in chunks:
                    stmt = (
                        update(ChunkModel)
                        .where(ChunkModel.id == chunk.id)
                        .values(
                            chunk=chunk.chunk,
                            embedding=chunk.embedding,
                            page_number=chunk.page_number,
                            type=chunk.type,
                            updated_at=chunk.updated_at,
                        )
                    )
                    await session.execute(stmt)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to update chunks: {e!s}")

    async def insert_document_and_chunks(self, document: Document) -> Document:
        """Insert a document and its associated chunks into the database.

        Args:
            document: The Document model to insert

        Returns:
            Document: The inserted document with updated IDs
        """
        async with SessionLocal() as session:
            try:
                # insert document data
                stmt = (
                    insert(DocumentModel)
                    .values(
                        name=document.name,
                        tenant_id=document.tenant_id,
                        status=document.status,
                        type=document.type,
                        created_at=document.created_at,
                        updated_at=document.updated_at,
                    )
                    .returning(DocumentModel.id)
                )

                result = await session.execute(stmt)
                document_id = result.scalar_one()

                # insert chunks data
                values = [
                    {
                        "type": chunk.type,
                        "chunk": chunk.chunk,
                        "tenant_id": document.tenant_id,
                        "page_number": chunk.page_number,
                        "embedding": chunk.embedding,
                        "document_id": document_id,
                    }
                    for chunk in document.chunks
                ]

                stmt = insert(ChunkModel).values(values)
                await session.execute(stmt)
                await session.commit()

            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to insert document and chunks: {e!s}")

            document = await self.get_document(tenant_id=document.tenant_id, document_id=document_id)
            return document

    async def delete_document_and_chunks(self, document_id: str) -> None:
        """Delete a document and its associated chunks from the database.

        Args:
            document_id: The ID of the document to delete

        """
        async with SessionLocal() as session:
            try:
                await session.execute(delete(ChunkModel).where(ChunkModel.document_id == document_id))
                await session.execute(delete(DocumentModel).where(DocumentModel.id == document_id))
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to delete document and chunks: {e!s}")

    async def remove_tenant_content(self, tenant_id: str) -> None:
        """Remove all content for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose content should be removed
        """

        async with SessionLocal() as session:
            try:
                await session.execute(delete(DocumentModel).where(DocumentModel.tenant_id == tenant_id))
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to remove tenant content: {e!s}")
