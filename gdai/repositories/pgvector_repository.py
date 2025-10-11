"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, desc, insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from gdai.commons.enums import QueryStatusEnum
from gdai.commons.logger import logger

from .base_repository import BaseRepository
from .database import DatabaseManager
from .models import ChunkModel, DocumentModel, QueryChunkLinkModel, QueryModel


class PGVectorRepository(BaseRepository):
    """Repository for managing documents and chunks in PostgreSQL with pgvector.

    This repository can be used in two ways:
    1. With automatic session management (context manager):
        async with PGVectorRepository() as repo:
            doc = await repo.get_document(tenant_id, doc_id)

    2. With provided session (for transactions):
        async with DatabaseManager.create_session() as session:
            repo = PGVectorRepository(session)
            await repo.insert_document(doc)
    """

    def __init__(self, session: AsyncSession | None = None):
        """Initialize the PGVector Repository.

        Args:
            session: Optional database session. If not provided, repository will
                    manage its own session lifecycle.
        """
        super().__init__()
        self._session = session
        self._owns_session = session is None

    async def __aenter__(self):
        """Enter async context manager."""
        if self._owns_session:
            self._session = await DatabaseManager.create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self._owns_session and self._session:
            if exc_type is not None:
                await self._session.rollback()
            await self._session.close()
            self._session = None

    def _get_session(self) -> AsyncSession:
        """Get the current session.

        Returns:
            AsyncSession: The current database session.

        Raises:
            RuntimeError: If no session is available.
        """
        if self._session is None:
            raise RuntimeError(
                "No session available. Use repository as context manager: "
                "async with PGVectorRepository() as repo: ..."
            )
        return self._session

    async def get_all_documents(self, tenant_id: str) -> list[DocumentModel]:
        """Retrieve all documents for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose documents to retrieve.

        Returns:
            list[DocumentModel]: List of document models belonging to the tenant.
        """
        session = self._get_session()
        query = select(DocumentModel).where(DocumentModel.tenant_id == tenant_id)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_document(self, tenant_id: str, document_id: str) -> DocumentModel | None:
        """Retrieve a specific document by ID for a tenant.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document to retrieve.

        Returns:
            Optional[DocumentModel]: The requested document or None if not found.
        """
        session = self._get_session()
        query = select(DocumentModel).where(
            DocumentModel.tenant_id == tenant_id, DocumentModel.id == uuid.UUID(document_id)
        )
        result = await session.execute(query)
        return result.scalars().first()

    async def insert_document(self, document: DocumentModel) -> DocumentModel:
        """Insert a new document into the database.

        Args:
            document: The document model to insert.

        Returns:
            DocumentModel: The inserted document with updated fields.
        """
        session = self._get_session()
        session.add(document)
        await session.commit()
        await session.refresh(document)
        return document

    async def delete_document(self, tenant_id: str, document_id: str) -> bool:
        """Delete a specific document by ID for a tenant.

        This method first deletes all chunks associated with the document
        to handle the foreign key constraint, then deletes the document itself.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document to delete.

        Returns:
            bool: True if document was deleted, False if not found.
        """
        session = self._get_session()
        doc_uuid = uuid.UUID(document_id)

        # First, delete all chunks associated with this document
        chunks_stmt = delete(ChunkModel).where(ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == doc_uuid)
        await session.execute(chunks_stmt)

        # Then delete the document itself
        doc_stmt = delete(DocumentModel).where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == doc_uuid)
        result = await session.execute(doc_stmt)
        await session.commit()
        return result.rowcount > 0

    async def insert_chunks(self, chunks: list[ChunkModel]) -> None:
        """Insert multiple chunks into the database in batches.

        Args:
            chunks: List of chunk models to insert.
        """
        if not chunks:
            return

        session = self._get_session()
        batch_size = 128

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            session.add_all(batch)
            await session.commit()

    async def insert_batch_chunks(self, chunks: list[ChunkModel]) -> None:
        """Insert multiple chunks using batch insert statement.

        Args:
            chunks: List of chunk models to insert.
        """
        if not chunks:
            return

        session = self._get_session()

        # Convert models to dicts for bulk insert
        chunk_dicts = [
            {
                "id": chunk.id,
                "tenant_id": chunk.tenant_id,
                "document_id": chunk.document_id,
                "type": chunk.type,
                "chunk": chunk.chunk,
                "page_number": chunk.page_number,
                "embedding": chunk.embedding,
            }
            for chunk in chunks
        ]

        stmt = insert(ChunkModel).values(chunk_dicts)
        await session.execute(stmt)
        await session.commit()

    async def get_chunks(self, tenant_id: str, document_id: str) -> list[ChunkModel]:
        """Retrieve all chunks for a specific document.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document.

        Returns:
            list[ChunkModel]: List of chunk models for the document.
        """
        session = self._get_session()
        query = select(ChunkModel).where(
            ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == uuid.UUID(document_id)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_chunks_without_embedding(self, tenant_id: str, batch_size: int = 20) -> list[ChunkModel]:
        """Retrieve chunks that don't have embeddings yet.

        Args:
            tenant_id: The ID of the tenant.
            batch_size: Maximum number of chunks to retrieve.

        Returns:
            list[ChunkModel]: List of chunks without embeddings.
        """
        session = self._get_session()
        query = (
            select(ChunkModel)
            .where(ChunkModel.tenant_id == tenant_id, ChunkModel.embedding.is_(None))
            .limit(batch_size)
        )
        result = await session.execute(query)
        return list(result.scalars().all())

    async def delete_chunks(self, tenant_id: str, document_id: str) -> int:
        """Delete all chunks for a specific document.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document.

        Returns:
            int: Number of chunks deleted.
        """
        session = self._get_session()
        stmt = delete(ChunkModel).where(
            ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == uuid.UUID(document_id)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount

    async def update_chunks(self, chunks: list[ChunkModel]) -> None:
        """Update multiple chunks in the database.

        Args:
            chunks: List of chunk models to update.
        """
        if not chunks:
            return

        session = self._get_session()
        batch_size = 128

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            for chunk in batch:
                await session.merge(chunk)
            await session.commit()

    async def insert_query(self, query: QueryModel) -> QueryModel:
        """Insert a new query into the database.

        Args:
            query: The query model to insert.

        Returns:
            QueryModel: The inserted query with updated fields.
        """
        session = self._get_session()
        session.add(query)
        await session.commit()
        await session.refresh(query)
        return query

    async def update_query_result(
        self, tenant_id: str, query_id: str, result: str, status: str = "completed"
    ) -> QueryModel:
        """Update the result and status of a specific query.

        Args:
            tenant_id: The ID of the tenant.
            query_id: The ID of the query to update.
            result: The result text to set for the query.
            status: The new status of the query.

        Returns:
            QueryModel: The updated query.

        Raises:
            ValueError: If query not found.
        """
        session = self._get_session()
        query_status = QueryStatusEnum(status)

        stmt = select(QueryModel).where(QueryModel.tenant_id == tenant_id, QueryModel.id == uuid.UUID(query_id))
        query_result = await session.execute(stmt)
        query_model = query_result.scalars().first()

        if not query_model:
            raise ValueError(f"Query with ID {query_id} not found for tenant {tenant_id}.")

        query_model.result = result
        query_model.status = query_status
        await session.commit()
        await session.refresh(query_model)
        return query_model

    async def get_query(self, tenant_id: str, query_id: str) -> QueryModel | None:
        """Retrieve a specific query by ID for a tenant.

        Args:
            tenant_id: The ID of the tenant.
            query_id: The ID of the query to retrieve.

        Returns:
            Optional[QueryModel]: The requested query or None if not found.
        """
        session = self._get_session()
        stmt = select(QueryModel).where(QueryModel.tenant_id == tenant_id, QueryModel.id == uuid.UUID(query_id))
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_all_queries(self, tenant_id: str) -> list[QueryModel]:
        """Retrieve all queries for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose queries to retrieve.

        Returns:
            list[QueryModel]: List of query models belonging to the tenant.
        """
        session = self._get_session()
        stmt = select(QueryModel).where(QueryModel.tenant_id == tenant_id).order_by(QueryModel.created_at.desc())
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def search_chunks_by_similarity_on_document_ids(
        self,
        tenant_id: str,
        query_vector: list[float],
        similarity_threshold: float,
        document_ids: list[str],
        limit: int = 10,
    ) -> list[tuple[ChunkModel, float]]:
        """Search for chunks by vector similarity within specific documents.

        Args:
            tenant_id: The ID of the tenant to search within.
            query_vector: The embedding vector to compare against chunks.
            similarity_threshold: The minimum similarity score (0-1) for results.
            document_ids: List of document IDs to restrict search to.
            limit: The maximum number of results to return.

        Returns:
            list[tuple[ChunkModel, float]]: List of tuples with chunks and similarity scores.
        """
        session = self._get_session()

        # Calculate distance and similarity expressions
        distance_expr = ChunkModel.embedding.cosine_distance(query_vector)
        similarity_expr = (1.0 - distance_expr).label("similarity")

        stmt = (
            select(ChunkModel, similarity_expr)
            .where(ChunkModel.tenant_id == tenant_id, similarity_expr >= similarity_threshold)
            .order_by(desc(similarity_expr))
            .limit(limit)
        )

        if document_ids:
            stmt = stmt.where(ChunkModel.document_id.in_([uuid.UUID(doc_id) for doc_id in document_ids]))

        result = await session.execute(stmt)
        results = result.all()

        if not results:
            logger.warning("No chunks found matching the criteria.")
            return []

        return results

    async def insert_query_chunk_links(
        self, tenant_id: str, query_id: str, chunks_ids_with_similarity: list[tuple[str, float]]
    ) -> None:
        """Insert links between a query and related chunks with similarity scores.

        Args:
            tenant_id: The ID of the tenant.
            query_id: The ID of the query.
            chunks_ids_with_similarity: List of tuples (chunk_id, similarity_score).
        """
        if not chunks_ids_with_similarity:
            return

        session = self._get_session()

        stmt = insert(QueryChunkLinkModel).values(
            [
                {
                    "id": uuid.uuid4(),
                    "tenant_id": tenant_id,
                    "query_id": query_id,
                    "chunk_id": chunk_id,
                    "similarity_score": similarity,
                }
                for (chunk_id, similarity) in chunks_ids_with_similarity
            ]
        )
        await session.execute(stmt)
        await session.commit()
