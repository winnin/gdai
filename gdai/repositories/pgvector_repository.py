"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, desc, insert, select

from gdai.commons.enums import QueryStatusEnum
from gdai.commons.logger import logger

from .base_repository import BaseRepository
from .models import ChunkModel, DocumentModel, QueryChunkLinkModel, QueryModel
from .sqlalchemy import SessionLocal


class PGVectorRepository(BaseRepository):
    """Repository for managing documents and chunks in PostgreSQL with pgvector."""

    def __init__(self):
        """Initialize the PGVector Repository.
        Extends the BaseRepository initialization.
        """
        super().__init__()

    async def get_all_documents(self, tenant_id: str) -> list[DocumentModel]:
        """Retrieve all documents for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose documents to retrieve.

        Returns:
            list[DocumentModel]: List of document models belonging to the tenant.

        Raises:
            ValueError: If there's an error retrieving the documents.
        """
        async with SessionLocal() as session:
            try:
                query = select(DocumentModel).where(DocumentModel.tenant_id == tenant_id)
                result = await session.execute(query)
                documents_model = result.scalars().all()
                return documents_model
            except Exception as e:
                raise ValueError(f"Failed to retrieve documents: {e!s}")

    async def get_document(self, tenant_id: str, document_id: str) -> DocumentModel:
        """Retrieve a specific document by ID for a tenant.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document to retrieve.

        Returns:
            DocumentModel: The requested document.

        Raises:
            ValueError: If the document is not found or there's an error retrieving it.
        """
        async with SessionLocal() as session:
            try:
                query = select(DocumentModel).where(
                    DocumentModel.tenant_id == tenant_id, DocumentModel.id == uuid.UUID(document_id)
                )
                result = await session.execute(query)
                document_model = result.scalars().first()
                if not document_model:
                    raise ValueError(f"DocumentModel with ID {document_id} not found for tenant {tenant_id}.")
                return document_model
            except Exception as e:
                raise ValueError(f"Failed to retrieve document: {e!s}")

    async def insert_document(self, document: DocumentModel) -> None:
        """Insert a new document into the database.

        Args:
            document: The document model to insert.

        Raises:
            ValueError: If there's an error inserting the document.
        """
        async with SessionLocal() as session:
            try:
                session.add(document)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to insert document: {e!s}")

    async def delete_document(self, tenant_id: str, document_id: str) -> None:
        """Delete a specific document by ID for a tenant.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document to delete.

        Raises:
            ValueError: If there's an error deleting the document.
        """
        async with SessionLocal() as session:
            try:
                await session.execute(
                    delete(DocumentModel)
                    .where(DocumentModel.tenant_id == tenant_id)
                    .where(DocumentModel.id == document_id)
                )
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to delete document: {e!s}")

    async def insert_chunks(self, chunks: list[ChunkModel]) -> None:
        """Insert multiple chunks into the database in batches.

        Args:
            chunks: List of chunk models to insert.

        Raises:
            ValueError: If there's an error inserting the chunks.
        """
        batch_size = 128
        async with SessionLocal() as session:
            try:
                for i in range(0, len(chunks), batch_size):
                    session.add_all(chunks[i : i + batch_size])
                    await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to insert document: {e!s}")

    async def get_chunks(self, tenant_id: str, document_id: str) -> list[ChunkModel]:
        """Retrieve all chunks for a specific document of a tenant.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document whose chunks to retrieve.

        Returns:
            list[ChunkModel]: List of chunk models belonging to the document.

        Raises:
            ValueError: If no chunks are found or there's an error retrieving them.
        """
        async with SessionLocal() as session:
            try:
                query = select(ChunkModel).where(
                    ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == document_id
                )
                result = await session.execute(query)
                chunks_model = result.scalars().all()
                if not chunks_model:
                    raise ValueError(f"No chunks found for document ID {document_id} in tenant {tenant_id}.")
                return chunks_model
            except Exception as e:
                raise ValueError(f"Failed to retrieve chunks: {e!s}")

    async def get_chunks_without_embedding(self, batch_size: int) -> list[ChunkModel]:
        """Retrieve chunks that do not have embeddings yet.

        Args:
            batch_size: The maximum number of chunks to retrieve.

        Returns:
            list[ChunkModel]: List of chunk models without embeddings.

        Raises:
            ValueError: If there's an error retrieving the chunks.
        """
        async with SessionLocal() as session:
            try:
                query = select(ChunkModel).where(ChunkModel.embedding.is_(None)).limit(batch_size)
                result = await session.execute(query)
                chunks_model = result.scalars().all()
                return chunks_model
            except Exception as e:
                raise ValueError(f"Failed to retrieve chunks without embeddings: {e!s}") from e

    async def delete_chunks(self, tenant_id: str, document_id: str) -> None:
        """Delete all chunks for a specific document of a tenant.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document whose chunks to delete.

        Raises:
            ValueError: If there's an error deleting the chunks.
        """
        async with SessionLocal() as session:
            try:
                stmt = delete(ChunkModel).where(
                    ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == document_id
                )
                await session.execute(stmt)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to delete chunks: {e!s}")

    async def update_chunks(self, chunks: list[ChunkModel]) -> None:
        """Update multiple chunks in the database in batches.

        Args:
            chunks: List of chunk models to update.

        Raises:
            ValueError: If there's an error updating the chunks.
        """
        batch_size = 128
        async with SessionLocal() as session:
            try:
                for i in range(0, len(chunks), batch_size):
                    session.add_all(chunks[i : i + batch_size])
                    await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to update chunks: {e!s}")

    async def insert_query(self, query: QueryModel) -> None:
        """Insert a new query into the database.

        Args:
            query: The query model to insert.

        Raises:
            ValueError: If there's an error inserting the query.
        """
        async with SessionLocal() as session:
            try:
                session.add(query)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to insert query: {e!s}")

    async def update_query_result(self, query_id: str, tenant_id: str, result: str, status: str) -> None:
        """Update the result and status of a specific query.

        Args:
            query_id: The ID of the query to update.
            tenant_id: The ID of the tenant.
            result: The result text to set for the query.
            status: The new status of the query.
        Raises:
            ValueError: If there's an error updating the query.
        """

        async with SessionLocal() as session:
            try:
                status = QueryStatusEnum(status)
                stmt = (
                    select(QueryModel)
                    .where(QueryModel.tenant_id == tenant_id)
                    .where(QueryModel.id == uuid.UUID(query_id))
                )
                result_query = await session.execute(stmt)
                query_model = result_query.scalars().first()
                if not query_model:
                    raise ValueError(f"Query with ID {query_id} not found for tenant {tenant_id}.")
                query_model.result = result
                query_model.status = status
                session.add(query_model)
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to update query result: {e!s}") from e

    async def search_chunks_by_similarity_on_document_ids(
        self,
        tenant_id: str,
        query_vector: list[float],
        similarity_threshold: float,
        document_ids: list[str],
        limit: int = 10,
    ) -> list[tuple[ChunkModel, float]]:
        """Search for chunks by vector similarity within specific set of documents if they are defined.

        Args:
            tenant_id: The ID of the tenant to search within.
            query_id: The ID of the query being performed.
            query_vector: The embedding vector to compare against chunks.
            document_ids: List of document IDs to restrict the search to.
            similarity_threshold: The minimum similarity score (0-1) for returned results.
            limit: The maximum number of results to return.

        Returns:
            list[tuple[ChunkModel, float]]: List of tuples containing chunks and their similarity scores.

        Raises:
            ValueError: If no chunks meet the criteria or there's an error.
        """

        async with SessionLocal() as session:
            try:
                # Calculate distance expression
                distance_expr = ChunkModel.embedding.cosine_distance(query_vector)

                # Calculate similarity expression (1 - distance)
                similarity_expr = (1.0 - distance_expr).label("similarity")
                stmt = (
                    select(ChunkModel, similarity_expr)
                    .where(ChunkModel.tenant_id == tenant_id)
                    .where(similarity_expr >= similarity_threshold)
                    .order_by(desc(similarity_expr))
                    .limit(limit)
                )
                if document_ids:
                    stmt = stmt.where(ChunkModel.document_id.in_(document_ids))

                result = await session.execute(stmt)
                result = result.all()

                if not result:
                    logger.warning("No chunks found matching the criteria.")
                    return []
                return result
            except Exception as e:
                raise ValueError(f"Failed to search chunks by similarity and document IDs: {e!s}")

    async def insert_query_chunk_links(self, tenant_id: str, query_id: str, chunks_ids_with_similarity: list) -> None:
        try:
            async with SessionLocal() as session:
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
        except Exception as e:
            raise ValueError(f"Failed to insert query-chunk links: {e!s}")

    async def get_query(self, tenant_id: str, query_id: str) -> QueryModel:
        """Retrieve a specific query by ID for a tenant.

        Args:
            tenant_id: The ID of the tenant.
            query_id: The ID of the query to retrieve.

        Returns:
            QueryModel: The requested query.

        Raises:
            ValueError: If the query is not found or there's an error retrieving it.
        """
        async with SessionLocal() as session:
            try:
                stmt = (
                    select(QueryModel)
                    .where(QueryModel.tenant_id == tenant_id)
                    .where(QueryModel.id == uuid.UUID(query_id))
                )
                result = await session.execute(stmt)
                query_model = result.scalars().first()
                if not query_model:
                    raise ValueError(f"Query with ID {query_id} not found for tenant {tenant_id}.")
                return query_model
            except Exception as e:
                raise ValueError(f"Failed to retrieve query: {e!s}")
