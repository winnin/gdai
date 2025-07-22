"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from src.config.logger import logger
from src.config.sqlalchemy import SessionLocal
from src.repositories.base import DocumentChunkRepository, DocumentRepository, QueryRepository
from src.repositories.models import ChunkTypeEnum, DocumentChunkModel, DocumentModel, DocumentStatusEnum, DocumentTypeEnum, QueryModel
from src.schemas import Document, DocumentChunk, Query


class PGVectorDocumentRepository(DocumentRepository):
    """Manages documents and chunks in a PostgreSQL database with SQLAlchemy."""

    async def get_all(self, tenant_id: str):
        async with SessionLocal() as session:
            result = await session.execute(select(DocumentModel).where(DocumentModel.tenant_id == tenant_id))
            docs = result.scalars().all()
            return [Document.model_validate(doc) for doc in docs]

    async def get_by_id(self, tenant_id: str, document_id: str):
        async with SessionLocal() as session:
            result = await session.execute(select(DocumentModel).where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document_id))
            doc = result.scalar_one_or_none()
            return Document.model_validate(doc) if doc else None

    async def insert(self, tenant_id: str, document: Document):
        try:
            async with SessionLocal() as session:
                db_doc = DocumentModel(id=document.id, tenant_id=tenant_id, name=document.name, status=DocumentStatusEnum[document.status], type=DocumentTypeEnum[document.type])
                session.add(db_doc)
                await session.commit()

        except Exception as e:
            logger.error(f"Error inserting document: {e}")

    async def update(self, tenant_id: str, document: Document):
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentModel).where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document.id))
                db_doc = result.scalar_one_or_none()
                if db_doc:
                    db_doc.name = document.name
                    db_doc.status = document.status
                    db_doc.type = document.type
                    await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error updating document: {e}")

    async def delete(self, tenant_id: str, document_id: str):
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentModel).where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document_id))
                db_doc = result.scalar_one_or_none()
                if db_doc:
                    await session.delete(db_doc)
                    await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error deleting document: {e}")

    async def delete_all(self, tenant_id: str):
        try:
            async with SessionLocal() as session:
                await session.execute(DocumentModel.__table__.delete().where(DocumentModel.tenant_id == tenant_id))
                await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error deleting all documents: {e}")


class PGVectorDocumentChunkRepository(DocumentChunkRepository):
    """Manages document chunks in a PostgreSQL database with SQLAlchemy."""

    async def get_all(self, tenant_id: str):
        async with SessionLocal() as session:
            result = await session.execute(select(DocumentChunkModel).where(DocumentChunkModel.tenant_id == tenant_id))
            chunks = result.scalars().all()
            return [DocumentChunk.model_validate(chunk) for chunk in chunks]

    async def get_by_id(self, tenant_id: str, document_chunk_id: str):
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentChunkModel).where(DocumentChunkModel.tenant_id == tenant_id, DocumentChunkModel.id == document_chunk_id))
                chunk = result.scalar_one_or_none()
                return DocumentChunk.model_validate(chunk) if chunk else None
        except Exception as e:
            logger.error(f"Error getting document chunk: {e}")

    async def insert(self, tenant_id: str, chunk: DocumentChunk):
        try:
            async with SessionLocal() as session:
                db_chunk = DocumentChunkModel(
                    id=chunk.id,
                    tenant_id=tenant_id,
                    type=ChunkTypeEnum[chunk.type],
                    chunk=chunk.chunk,
                    page_number=chunk.page_number,
                    embedding=chunk.embedding,
                    document_id=chunk.document_id,
                )
                session.add(db_chunk)
                await session.commit()
        except Exception as e:
            logger.error(f"Error inserting document chunk: {e}")

    async def insert_batch(self, tenant_id: str, items: list[DocumentChunk]):
        try:
            async with SessionLocal() as session:
                db_chunks = [
                    DocumentChunkModel(
                        id=chunk.id,
                        tenant_id=tenant_id,
                        type=chunk.type,
                        chunk=chunk.chunk,
                        page_number=chunk.page_number,
                        embedding=chunk.embedding,
                        document_id=chunk.document_id,
                        created_at=chunk.created_at,
                        updated_at=chunk.updated_at,
                    )
                    for chunk in items
                ]
                session.add_all(db_chunks)
                await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error inserting batch of document chunks: {e}")

    async def update(self, tenant_id: str, chunk: DocumentChunk):
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentChunkModel).where(DocumentChunkModel.tenant_id == tenant_id, DocumentChunkModel.id == chunk.id))
                db_chunk = result.scalar_one_or_none()
                if db_chunk:
                    db_chunk.type = chunk.type
                    db_chunk.chunk = chunk.chunk
                    db_chunk.page_number = chunk.page_number
                    db_chunk.embedding = chunk.embedding
                    db_chunk.updated_at = chunk.updated_at
                    await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error updating document chunk: {e}")

    async def update_batch(self, tenant_id: str, items: list[DocumentChunk]):
        try:
            async with SessionLocal() as session:
                for chunk in items:
                    result = await session.execute(select(DocumentChunkModel).where(DocumentChunkModel.tenant_id == tenant_id, DocumentChunkModel.id == chunk.id))
                    db_chunk = result.scalar_one_or_none()
                    if db_chunk:
                        db_chunk.type = chunk.type
                        db_chunk.chunk = chunk.chunk
                        db_chunk.page_number = chunk.page_number
                        db_chunk.embedding = chunk.embedding
                        db_chunk.updated_at = chunk.updated_at
                await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error updating batch of document chunks: {e}")

    async def delete(self, tenant_id: str, document_chunk_id: str):
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentChunkModel).where(DocumentChunkModel.tenant_id == tenant_id, DocumentChunkModel.id == document_chunk_id))
                db_chunk = result.scalar_one_or_none()
                if db_chunk:
                    await session.delete(db_chunk)
                    await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error deleting document chunk: {e}")

    async def delete_all(self, tenant_id: str):
        try:
            async with SessionLocal() as session:
                await session.execute(DocumentChunkModel.__table__.delete().where(DocumentChunkModel.tenant_id == tenant_id))
                await session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error deleting all document chunks: {e}")

    async def get_by_document_id(self, tenant_id: str, document_id: str):
        async with SessionLocal() as session:
            result = await session.execute(select(DocumentChunkModel).where(DocumentChunkModel.tenant_id == tenant_id, DocumentChunkModel.document_id == document_id))
            chunks = result.scalars().all()
            return [DocumentChunk.model_validate(chunk) for chunk in chunks]

    async def search_by_similarity(self, tenant_id: str, vector: list[float], similarity_threshold: float = 0.8, limit: int = 30):
        """Search for document chunks by similarity to a given vector."""
        async with SessionLocal() as session:
            result = await session.execute(
                select(DocumentChunkModel)
                .where(DocumentChunkModel.tenant_id == tenant_id, DocumentChunkModel.embedding.op("vector_similarity")(vector) > similarity_threshold)
                .limit(limit)
            )
            chunks = result.scalars().all()
            return [DocumentChunk.model_validate(chunk) for chunk in chunks]

    async def search_by_similarity_on_specific_documents(self, tenant_id: str, vector: list[float], document_ids: list[str], similarity_threshold: float = 0.8, limit: int = 30):
        """Search for document chunks by similarity to a given vector within specific documents."""
        async with SessionLocal() as session:
            result = await session.execute(
                select(DocumentChunkModel)
                .where(
                    DocumentChunkModel.tenant_id == tenant_id,
                    DocumentChunkModel.document_id.in_(document_ids),
                    DocumentChunkModel.embedding.op("vector_similarity")(vector) > similarity_threshold,
                )
                .limit(limit)
            )
            chunks = result.scalars().all()
            return [DocumentChunk.model_validate(chunk) for chunk in chunks]


class PGVectorQueryRepository(QueryRepository):
    """Manages queries in a PostgreSQL database with SQLAlchemy."""

    async def get_all(self, tenant_id: str):
        async with SessionLocal() as session:
            result = await session.execute(select(QueryModel).where(QueryModel.tenant_id == tenant_id))
            queries = result.scalars().all()
            return [Query.model_validate(q) for q in queries]

    async def get_by_id(self, tenant_id: str, query_id: str):
        async with SessionLocal() as session:
            result = await session.execute(select(QueryModel).where(QueryModel.tenant_id == tenant_id, QueryModel.id == query_id))
            query = result.scalar_one_or_none()
            return Query.model_validate(query) if query else None

    async def insert(self, tenant_id: str, query: Query):
        async with SessionLocal() as session:
            db_query = QueryModel(
                id=query.id,
                tenant_id=tenant_id,
                query=query.query,
                result=query.result,
                status=query.status,
                created_at=query.created_at,
                updated_at=query.updated_at,
            )
            session.add(db_query)
            await session.commit()

    async def update(self, tenant_id: str, query: Query):
        async with SessionLocal() as session:
            result = await session.execute(select(QueryModel).where(QueryModel.tenant_id == tenant_id, QueryModel.id == query.id))
            db_query = result.scalar_one_or_none()
            if db_query:
                db_query.query = query.query
                db_query.result = query.result
                db_query.status = query.status
                db_query.updated_at = query.updated_at
                await session.commit()

    async def delete(self, tenant_id: str, query_id: str):
        async with SessionLocal() as session:
            result = await session.execute(select(QueryModel).where(QueryModel.tenant_id == tenant_id, QueryModel.id == query_id))
            db_query = result.scalar_one_or_none()
            if db_query:
                await session.delete(db_query)
                await session.commit()

    async def delete_all(self, tenant_id: str):
        async with SessionLocal() as session:
            await session.execute(QueryModel.__table__.delete().where(QueryModel.tenant_id == tenant_id))
            await session.commit()
