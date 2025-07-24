"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from gdai.config.logger import logger
from gdai.config.sqlalchemy import SessionLocal
from gdai.repositories.base import DocumentRepository
from gdai.repositories.models import DocumentModel
from gdai.schemas import Document


class PGVectorDocumentRepository(DocumentRepository):
    """Manages documents and chunks in a PostgreSQL database with SQLAlchemy."""

    async def get_all(self, tenant_id: str) -> list[Document]:
        """Get all documents for a tenant."""
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentModel).where(DocumentModel.tenant_id == tenant_id))
                docs = result.scalars().all()
                return [Document.model_validate(doc.__dict__) for doc in docs]
        except SQLAlchemyError as e:
            logger.error(f"Error getting all documents: {e}")
            return []

    async def get_by_id(self, tenant_id: str, document_id: str) -> Document | None:
        """Get a document by its ID."""
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentModel).where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document_id))
                doc = result.scalar_one_or_none()
                return Document.model_validate(doc.__dict__) if doc else None
        except SQLAlchemyError as e:
            logger.error(f"Error getting document by ID: {e}")
            return None

    async def insert(self, tenant_id: str, document: Document) -> bool:
        """Insert a new document."""
        try:
            async with SessionLocal() as session:
                db_doc = DocumentModel(id=document.id, tenant_id=tenant_id, name=document.name, status=document.status, type=document.type, chunks=[])

                session.add(db_doc)
                await session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error inserting document: {e}")
            return False

    async def update(self, tenant_id: str, document: Document) -> bool:
        """Update an existing document."""
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentModel).where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document.id))
                db_doc = result.scalar_one_or_none()
                if db_doc:
                    db_doc.name = document.name
                    db_doc.status = document.status
                    db_doc.type = document.type
                    await session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Error updating document: {e}")
            return False

    async def delete(self, tenant_id: str, document_id: str) -> bool:
        """Delete a document."""
        try:
            async with SessionLocal() as session:
                result = await session.execute(select(DocumentModel).where(DocumentModel.tenant_id == tenant_id, DocumentModel.id == document_id))
                db_doc = result.scalar_one_or_none()
                if db_doc:
                    await session.delete(db_doc)
                    await session.commit()
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"Error deleting document: {e}")
            return False

    async def delete_all(self, tenant_id: str) -> bool:
        """Delete all documents for a tenant."""
        try:
            async with SessionLocal() as session:
                await session.execute(DocumentModel.__table__.delete().where(DocumentModel.tenant_id == tenant_id))
                await session.commit()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error deleting all documents: {e}")
            return False


# class PGVectorChunkModelRepository(ChunkModelRepository):
#     """Manages document chunks in a PostgreSQL database with SQLAlchemy."""

#     async def get_all(self, tenant_id: str) -> list[ChunkModel]:
#         """Get all document chunks for a tenant."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(ChunkModel).where(ChunkModel.tenant_id == tenant_id))
#                 chunks = result.scalars().all()
#                 return [ChunkModel.model_validate(chunk.__dict__) for chunk in chunks]
#         except SQLAlchemyError as e:
#             logger.error(f"Error getting all document chunks: {e}")
#             return []

#     async def get_by_id(self, tenant_id: str, document_chunk_id: str) -> ChunkModel | None:
#         """Get a document chunk by its ID."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(ChunkModel).where(ChunkModel.tenant_id == tenant_id, ChunkModel.id == document_chunk_id))
#                 chunk = result.scalar_one_or_none()
#                 return ChunkModel.model_validate(chunk.__dict__) if chunk else None
#         except SQLAlchemyError as e:
#             logger.error(f"Error getting document chunk by ID: {e}")
#             return None

#     async def insert(self, tenant_id: str, chunk: ChunkModel) -> bool:
#         """Insert a new document chunk."""
#         try:
#             async with SessionLocal() as session:
#                 db_chunk = ChunkModel(
#                     id=chunk.id,
#                     tenant_id=tenant_id,
#                     type=ChunkTypeEnum[chunk.type,
#                     chunk=chunk.chunk,
#                     page_number=chunk.page_number,
#                     embedding=chunk.embedding,
#                     document_id=chunk.document_id,
#                 )
#                 session.add(db_chunk)
#                 await session.commit()
#                 return True
#         except SQLAlchemyError as e:
#             logger.error(f"Error inserting document chunk: {e}")
#             return False

#     async def insert_batch(self, tenant_id: str, items: list[ChunkModel]) -> bool:
#         """Insert multiple document chunks at once."""
#         try:
#             async with SessionLocal() as session:
#                 db_chunks = [
#                     ChunkModel(
#                         id=chunk.id,
#                         tenant_id=tenant_id,
#                         type=ChunkTypeEnum[chunk.type,
#                         chunk=chunk.chunk,
#                         page_number=chunk.page_number,
#                         embedding=chunk.embedding,
#                         document_id=chunk.document_id,
#                         created_at=chunk.created_at,
#                         updated_at=chunk.updated_at,
#                     )
#                     for chunk in items
#                 ]
#                 session.add_all(db_chunks)
#                 await session.commit()
#                 return True
#         except SQLAlchemyError as e:
#             logger.error(f"Error inserting batch of document chunks: {e}")
#             return False

#     async def update(self, tenant_id: str, chunk: ChunkModel) -> bool:
#         """Update an existing document chunk."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(ChunkModel).where(ChunkModel.tenant_id == tenant_id, ChunkModel.id == chunk.id))
#                 db_chunk = result.scalar_one_or_none()
#                 if db_chunk:
#                     db_chunk.type.value = ChunkTypeEnum[chunk.type
#                     db_chunk.chunk = chunk.chunk
#                     db_chunk.page_number = chunk.page_number
#                     db_chunk.embedding = chunk.embedding
#                     db_chunk.updated_at = chunk.updated_at
#                     await session.commit()
#                     return True
#                 return False
#         except SQLAlchemyError as e:
#             logger.error(f"Error updating document chunk: {e}")
#             return False

#     async def update_batch(self, tenant_id: str, items: list[ChunkModel]) -> bool:
#         """Update multiple document chunks at once."""
#         try:
#             async with SessionLocal() as session:
#                 for chunk in items:
#                     result = await session.execute(select(ChunkModel).where(ChunkModel.tenant_id == tenant_id, ChunkModel.id == chunk.id))
#                     db_chunk = result.scalar_one_or_none()
#                     if db_chunk:
#                         db_chunk.type.value = ChunkTypeEnum[chunk.type
#                         db_chunk.chunk = chunk.chunk
#                         db_chunk.page_number = chunk.page_number
#                         db_chunk.embedding = chunk.embedding
#                         db_chunk.updated_at = chunk.updated_at
#                 await session.commit()
#                 return True
#         except SQLAlchemyError as e:
#             logger.error(f"Error updating batch of document chunks: {e}")
#             return False

#     async def delete(self, tenant_id: str, document_chunk_id: str) -> bool:
#         """Delete a document chunk."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(ChunkModel).where(ChunkModel.tenant_id == tenant_id, ChunkModel.id == document_chunk_id))
#                 db_chunk = result.scalar_one_or_none()
#                 if db_chunk:
#                     await session.delete(db_chunk)
#                     await session.commit()
#                     return True
#                 return False
#         except SQLAlchemyError as e:
#             logger.error(f"Error deleting document chunk: {e}")
#             return False

#     async def delete_all(self, tenant_id: str) -> bool:
#         """Delete all document chunks for a tenant."""
#         try:
#             async with SessionLocal() as session:
#                 await session.execute(ChunkModel.__table__.delete().where(ChunkModel.tenant_id == tenant_id))
#                 await session.commit()
#                 return True
#         except SQLAlchemyError as e:
#             logger.error(f"Error deleting all document chunks: {e}")
#             return False

#     async def get_by_document_id(self, tenant_id: str, document_id: str) -> list[ChunkModel]:
#         """Get all chunks for a specific document."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(ChunkModel).where(ChunkModel.tenant_id == tenant_id, ChunkModel.document_id == document_id))
#                 chunks = result.scalars().all()
#                 return [ChunkModel.model_validate(chunk.__dict__) for chunk in chunks]
#         except SQLAlchemyError as e:
#             logger.error(f"Error getting chunks by document ID: {e}")
#             return []

#     async def search_by_similarity(self, tenant_id: str, vector: list[float], similarity_threshold: float = 0.8, limit: int = 30) -> list[ChunkModel]:
#         """Search for document chunks by similarity to a given vector."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(
#                     select(ChunkModel).where(ChunkModel.tenant_id == tenant_id, ChunkModel.embedding.op("vector_similarity")(vector) > similarity_threshold).limit(limit)
#                 )
#                 chunks = result.scalars().all()
#                 return [ChunkModel.model_validate(chunk.__dict__) for chunk in chunks]
#         except SQLAlchemyError as e:
#             logger.error(f"Error searching by similarity: {e}")
#             return []

#     async def search_by_similarity_on_specific_documents(
#         self, tenant_id: str, vector: list[float], document_ids: list[str], similarity_threshold: float = 0.8, limit: int = 30
#     ) -> list[ChunkModel]:
#         """Search for document chunks by similarity to a given vector within specific documents."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(
#                     select(ChunkModel)
#                     .where(
#                         ChunkModel.tenant_id == tenant_id,
#                         ChunkModel.document_id.in_(document_ids),
#                         ChunkModel.embedding.op("vector_similarity")(vector) > similarity_threshold,
#                     )
#                     .limit(limit)
#                 )
#                 chunks = result.scalars().all()
#                 return [ChunkModel.model_validate(chunk.__dict__) for chunk in chunks]
#         except SQLAlchemyError as e:
#             logger.error(f"Error searching by similarity on specific documents: {e}")
#             return []


# class PGVectorQueryRepository(QueryRepository):
#     """Manages queries in a PostgreSQL database with SQLAlchemy."""

#     async def get_all(self, tenant_id: str) -> list[Query]:
#         """Get all queries for a tenant."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(QueryModel).where(QueryModel.tenant_id == tenant_id))
#                 queries = result.scalars().all()
#                 return [Query.model_validate(q.__dict__) for q in queries]
#         except SQLAlchemyError as e:
#             logger.error(f"Error getting all queries: {e}")
#             return []

#     async def get_by_id(self, tenant_id: str, query_id: str) -> Query | None:
#         """Get a query by its ID."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(QueryModel).where(QueryModel.tenant_id == tenant_id, QueryModel.id == query_id))
#                 query = result.scalar_one_or_none()
#                 return Query.model_validate(query.__dict__) if query else None
#         except SQLAlchemyError as e:
#             logger.error(f"Error getting query by ID: {e}")
#             return None

#     async def insert(self, tenant_id: str, query: Query) -> bool:
#         """Insert a new query."""
#         try:
#             async with SessionLocal() as session:
#                 db_query = QueryModel(
#                     id=query.id,
#                     tenant_id=tenant_id,
#                     query=query.query,
#                     result=query.result,
#                     status=QueryStatusEnum[query.status,
#                     similarity=SimilarityTypeEnum[query.similarity] if query.similarity else SimilarityTypeEnum.cosine,
#                 )
#                 session.add(db_query)
#                 await session.commit()
#                 return True
#         except SQLAlchemyError as e:
#             logger.error(f"Error inserting query: {e}")
#             return False

#     async def update(self, tenant_id: str, query: Query) -> bool:
#         """Update an existing query."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(QueryModel).where(QueryModel.tenant_id == tenant_id, QueryModel.id == query.id))
#                 db_query = result.scalar_one_or_none()
#                 if db_query:
#                     db_query.query = query.query
#                     db_query.result = query.result
#                     db_query.status.value = QueryStatusEnum[query.status
#                     if query.similarity:
#                         db_query.similarity = SimilarityTypeEnum[query.similarity]
#                     db_query.updated_at = query.updated_at
#                     await session.commit()
#                     return True
#                 return False
#         except SQLAlchemyError as e:
#             logger.error(f"Error updating query: {e}")
#             return False

#     async def delete(self, tenant_id: str, query_id: str) -> bool:
#         """Delete a query."""
#         try:
#             async with SessionLocal() as session:
#                 result = await session.execute(select(QueryModel).where(QueryModel.tenant_id == tenant_id, QueryModel.id == query_id))
#                 db_query = result.scalar_one_or_none()
#                 if db_query:
#                     await session.delete(db_query)
#                     await session.commit()
#                     return True
#                 return False
#         except SQLAlchemyError as e:
#             logger.error(f"Error deleting query: {e}")
#             return False

#     async def delete_all(self, tenant_id: str) -> bool:
#         """Delete all queries for a tenant."""
#         try:
#             async with SessionLocal() as session:
#                 await session.execute(QueryModel.__table__.delete().where(QueryModel.tenant_id == tenant_id))
#                 await session.commit()
#                 return True
#         except SQLAlchemyError as e:
#             logger.error(f"Error deleting all queries: {e}")
#             return False
