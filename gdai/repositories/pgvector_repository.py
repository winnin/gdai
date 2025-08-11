"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, desc, func, insert, or_, select, update

from gdai.commons.enums import QueryStatusEnum, SimilarityTypeEnum
from gdai.config.sqlalchemy import SessionLocal
from gdai.mappers import ChunkMapper, DocumentMapper
from gdai.mappers.query_mapper import QueryMapper
from gdai.mappers.result_chunk_mapper import ResultChunkMapper
from gdai.repositories.base_repository import BaseRepository
from gdai.repositories.models import ChunkModel, DocumentModel, QueryChunkLinkModel, QueryModel
from gdai.schemas import Chunk, Document, Query, ResultChunk


class PGVectorRepository(BaseRepository):
    """Repository for managing documents and chunks in PostgreSQL with pgvector."""

    def __init__(self):
        super().__init__()

    async def get_documents_to_extract(self, limit: int = 5) -> list[Document]:
        """Get all documents that are pending extraction."""
        async with SessionLocal() as session:
            try:
                query = (
                    select(DocumentModel)
                    .where(DocumentModel.status == "uploaded")
                    .order_by(DocumentModel.created_at)
                    .limit(limit)
                )
                result = await session.execute(query)
                documents_model = result.scalars().all()
                if not documents_model:
                    return []
                documents = [DocumentMapper.to_schema(doc) for doc in documents_model]
                return documents
            except Exception as e:
                raise ValueError(f"Failed to retrieve documents: {e!s}")

    async def get_all_documents(self, tenant_id: str) -> list[Document]:
        """Get all documents for a specific tenant.
        Args:
            tenant_id: The ID of the tenant
        Returns:
            list[Document]: The list of documents for the tenant
        """
        async with SessionLocal() as session:
            try:
                query = select(DocumentModel).where(DocumentModel.tenant_id == tenant_id)
                result = await session.execute(query)
                documents_model = result.scalars().all()
                documents = [DocumentMapper.to_schema(doc) for doc in documents_model]
                return documents
            except Exception as e:
                raise ValueError(f"Failed to retrieve documents: {e!s}")

    async def get_document(self, tenant_id: str, document_id: str) -> Document:
        """Get a document by tenant ID and document ID.
        Args:
            tenant_id: The ID of the tenant
            document_id: The ID of the document
        Returns:
            Document: The retrieved document
        """

        async with SessionLocal() as session:
            try:
                query = select(DocumentModel).where(
                    DocumentModel.tenant_id == tenant_id, DocumentModel.id == uuid.UUID(document_id)
                )
                result = await session.execute(query)
                document_model = result.scalars().first()
                if not document_model:
                    raise ValueError(f"Document with ID {document_id} not found for tenant {tenant_id}.")
            except Exception as e:
                raise ValueError(f"Failed to retrieve document: {e!s}")

            document = DocumentMapper.to_schema(document_model)
            return document

    async def get_document_to_embed(self) -> Document:
        """Get a document that is pending embedding."""
        async with SessionLocal() as session:
            try:
                query = (
                    select(DocumentModel)
                    .where(or_(DocumentModel.status == "extracted", DocumentModel.status == "embedding"))
                    .order_by(DocumentModel.created_at)
                    .limit(1)
                )
                result = await session.execute(query)
                document_model = result.scalars().first()
                if not document_model:
                    return None
                document = DocumentMapper.to_schema(document_model)
                return document
            except Exception as e:
                raise ValueError(f"Failed to retrieve document for embedding: {e!s}")

    async def insert_document(self, tenant_id: str, document: Document) -> Document:
        """Insert a document into the database.

        Args:
            document: The Document model to insert

        Returns:
            Document: The inserted document with updated ID
        """
        async with SessionLocal() as session:
            try:
                stmt = (
                    insert(DocumentModel)
                    .values(
                        name=document.name,
                        tenant_id=tenant_id,
                        status=document.status,
                        type=document.type,
                        chunk_strategy=document.chunk_strategy,
                    )
                    .returning(DocumentModel.id)
                )
                result = await session.execute(stmt)
                document_id = result.scalar_one()
                document.id = document_id
                await session.commit()
                return document
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to insert document: {e!s}")

    async def update_document(self, tenant_id: str, document: Document) -> Document:
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
                    .where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document.id)
                    .values(
                        name=document.name,
                        status=document.status,
                        type=document.type,
                        retry_extraction=document.retry_extraction,
                        retry_embedding=document.retry_embedding,
                        chunk_strategy=document.chunk_strategy,
                        updated_at=document.updated_at,
                    )
                )
                await session.execute(stmt)
                await session.commit()
                document = await self.get_document(tenant_id=document.tenant_id, document_id=str(document.id))

                return document
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to update document: {e!s}")

    async def insert_chunks(self, tenant_id: str, document_id: str, chunks: list[Chunk]) -> list[Chunk]:
        """Insert chunks for a specific document into the database.

        Args:
            document: The Document model to insert

        Returns:
            Document: The inserted document with updated IDs
        """
        batch_size = 128
        async with SessionLocal() as session:
            try:
                for i in range(0, len(chunks), batch_size):
                    # insert chunks data
                    values = [
                        {
                            "type": chunk.type,
                            "chunk": chunk.chunk,
                            "tenant_id": tenant_id,
                            "page_number": chunk.page_number,
                            "embedding": chunk.embedding,
                            "document_id": uuid.UUID(document_id),
                        }
                        for chunk in chunks[i : i + batch_size]
                    ]
                    stmt = insert(ChunkModel).values(values)
                    await session.execute(stmt)
                    await session.commit()
                chunks = await self.get_chunks(tenant_id=tenant_id, document_id=document_id)
                return chunks

            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to insert document and chunks: {e!s}")

    async def get_chunks(self, tenant_id: str, document_id: str) -> list[Chunk]:
        """Get all chunks for a specific document.
        Args:
            tenant_id: The ID of the tenant
            document_id: The ID of the document
        Returns:
            list[Chunk]: The list of document chunks
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
                chunks = [ChunkMapper.to_schema(chunk) for chunk in chunks_model]
                return chunks
            except Exception as e:
                raise ValueError(f"Failed to retrieve chunks: {e!s}")

    async def get_number_of_chunks(self, tenant_id: str, document_id: str) -> int:
        """Get the number of chunks for a specific document.
        Args:
            tenant_id: The ID of the tenant
            document_id: The ID of the document
        Returns:
            int: The number of chunks for the document
        """
        async with SessionLocal() as session:
            try:
                stmt = (
                    select(func.count())
                    .select_from(ChunkModel)
                    .where(ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == document_id)
                )
                result = await session.execute(stmt)
                count = result.scalar_one() or 0
                return count or 0
            except Exception as e:
                raise ValueError(f"Failed to retrieve number of chunks: {e!s}")

    async def update_chunks(self, tenant_id: str, chunks: list[Document]) -> list[Chunk]:
        """Update chunks in the database.
        Args:
            chunks: A list of Document models to update
        Returns:
            list[Chunk]: The updated chunks
        """
        async with SessionLocal() as session:
            try:
                for chunk in chunks:
                    stmt = (
                        update(ChunkModel)
                        .where(ChunkModel.id == chunk.id)
                        .where(ChunkModel.tenant_id == tenant_id)
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
                chunks = await self.get_chunks(tenant_id=tenant_id, document_id=chunk.document_id)
                return chunks
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to update chunks: {e!s}")

    async def delete_chunks(self, tenant_id: str, document_id: str) -> bool:
        """Delete all chunks for a specific document.
        Args:
            tenant_id: The ID of the tenant
            document_id: The ID of the document
        Returns:
            bool: True if the operation was successful, False otherwise
        """
        async with SessionLocal() as session:
            try:
                stmt = delete(ChunkModel).where(
                    ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == document_id
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to delete chunks: {e!s}")

    async def delete_document_and_chunks(self, tenant_id: str, document_id: str) -> bool:
        """Delete a document and its associated chunks from the database.

        Args:
            document_id: The ID of the document to delete
        Returns:
            bool: True if the operation was successful, False otherwise

        """
        async with SessionLocal() as session:
            try:
                await session.execute(
                    delete(ChunkModel)
                    .where(ChunkModel.tenant_id == tenant_id)
                    .where(ChunkModel.document_id == document_id)
                )
                await session.execute(
                    delete(DocumentModel)
                    .where(DocumentModel.tenant_id == tenant_id)
                    .where(DocumentModel.id == document_id)
                )
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to delete document and chunks: {e!s}")

    async def delete_tenant_content(self, tenant_id: str) -> bool:
        """Remove all content for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose content should be removed

        Returns:
            bool: True if the operation was successful, False otherwise
        """

        async with SessionLocal() as session:
            try:
                await session.execute(delete(DocumentModel).where(DocumentModel.tenant_id == tenant_id))
                await session.commit()
                return True
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to remove tenant content: {e!s}")

    async def insert_query(self, tenant_id: str, query: str, similarity: SimilarityTypeEnum) -> str:
        """Insert a query into the database.

        Args:
            tenant_id: The ID of the tenant
            query: The query text

        Returns:
            str: The ID of the inserted query
        """
        async with SessionLocal() as session:
            try:
                stmt = (
                    insert(QueryModel)
                    .values(tenant_id=tenant_id, query=query, status=QueryStatusEnum.pending, similarity=similarity)
                    .returning(QueryModel.id)
                )
                result = await session.execute(stmt)
                await session.commit()
                query_id = result.scalar_one()
                return query_id
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to insert query: {e!s}")

    async def search_chunks_by_similarity(
        self, tenant_id: str, query_id: str, query_vector: list[float], similarity_threshold: float, limit: int = 10
    ) -> list[ResultChunk]:
        """Search for chunks similar (by cosine) to a given query using vector similarity.

        Args:
            tenant_id: The ID of the tenant
            query: The query text
            limit: The maximum number of chunks to return

        Returns:
            list[Chunk]: A list of chunks that are similar to the query
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
                result = await session.execute(stmt)
                chunks_model = result.all()
                # create the link between query and chunks
                if not chunks_model:
                    raise ValueError(f"No chunks found for tenant {tenant_id} with the given similarity threshold.")

                stmt = insert(QueryChunkLinkModel).values(
                    [
                        {"query_id": query_id, "chunk_id": chunk.id, "similarity_score": similarity}
                        for chunk, similarity in chunks_model
                    ]
                )

                await session.execute(stmt)
                await session.commit()
                chunks_result = [ResultChunkMapper.to_schema(model, similarity) for model, similarity in chunks_model]

                return chunks_result

            except Exception as e:
                raise ValueError(f"Failed to search chunks by similarity: {e!s}")

    async def update_query(self, tenant_id: str, query: Query):
        """Update a query in the database.

        Args:
            tenant_id: The ID of the tenant
            query: The Query model to update

        Returns:
            Query: The updated query
        """
        async with SessionLocal() as session:
            try:
                stmt = (
                    update(QueryModel)
                    .where(QueryModel.tenant_id == tenant_id)
                    .where(QueryModel.id == query.id)
                    .values(query=query.query, result=query.result, status=query.status, similarity=query.similarity)
                )
                await session.execute(stmt)
                await session.commit()
                query = await self.get_query(tenant_id=tenant_id, query_id=str(query.id))
                return query
            except Exception as e:
                await session.rollback()
                raise ValueError(f"Failed to update query: {e!s}")

    async def get_query(self, tenant_id: str, query_id: str) -> Query:
        """Get a query by tenant ID and query ID.

        Args:
            tenant_id: The ID of the tenant
            query_id: The ID of the query
        Returns:
            Query: The retrieved query
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

                return QueryMapper.to_schema(query_model)
            except Exception as e:
                raise ValueError(f"Failed to retrieve query: {e!s}")
