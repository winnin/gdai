"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

from src.config.database import PGVectorDatabase
from src.config.logger import logger
from src.repositories.base import DocumentChunkRepository, DocumentRepository, QueryRepository
from src.schemas.chunk import DocumentChunk
from src.schemas.document import Document
from src.schemas.query import Query


class PGVectorDocumentRepository(DocumentRepository):
    """Manages documents and chunks in a PostgreSQL database with pgvector."""

    def __init__(self):
        """Initialize repository."""

    async def get_all(self, tenant_id: str):
        """Get all documents for a specific tenant."""
        async with PGVectorDatabase.get_connection() as connection:
            results = await connection.fetch(
                """
                SELECT id,
                       tenant_id,
                       name,
                       status,
                       type,
                       created_at,
                       updated_at
                FROM document
                WHERE tenant_id = $1
                """,
                tenant_id,
            )
            return [
                Document(
                    id=result["id"],
                    tenant_id=result["tenant_id"],
                    name=result["name"],
                    status=result["status"],
                    type=result["type"],
                    created_at=result["created_at"],
                    updated_at=result["updated_at"],
                )
                for result in results
            ]

    async def get_by_id(self, tenant_id: str, document_id: str):
        """Get document by ID."""
        async with PGVectorDatabase.get_connection() as connection:
            result = await connection.fetchrow(
                """
                 SELECT id,
                       tenant_id,
                       name,
                       status,
                       type,
                       created_at,
                       updated_at
                FROM document
                WHERE id = $1 AND tenant_id = $2
                """,
                document_id,
                tenant_id,
            )
            if result is None:
                return None
            doc = Document(
                id=result["id"],
                tenant_id=result["tenant_id"],
                name=result["name"],
                status=result["status"],
                type=result["type"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
            return doc

    async def insert(self, tenant_id: str, document: Document):
        """Insert document and chunks into database."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        INSERT INTO document (id, tenant_id, name, status, type)
                        VALUES ($1, $2, $3, $4, $5)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        document.id,
                        tenant_id,
                        document.name,
                        document.status,
                        document.type,
                    )
        except Exception as e:
            logger.error(f"Error inserting document: {e}")

    async def update(self, tenant_id: str, document: Document):
        """Update document by ID."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        UPDATE document
                        SET name = $1, status = $2, type = $3, updated_at = NOW()
                        WHERE id = $4 AND tenant_id = $5
                        """,
                        document.name,
                        document.status,
                        document.type,
                        document.id,
                        tenant_id,
                    )
        except Exception as e:
            logger.error(f"Error updating document: {e}")

    async def delete(self, tenant_id: str, document_id: str):
        """Delete document by ID."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                await connection.execute(
                    """
                    DELETE FROM document
                    WHERE id = $1 AND tenant_id = $2
                    """,
                    document_id,
                    tenant_id,
                )
        except Exception as e:
            logger.error(f"Error deleting document: {e}")

    async def delete_all(self, tenant_id: str):
        """Delete all documents for a specific tenant."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                await connection.execute(
                    """
                    DELETE FROM document
                    WHERE tenant_id = $1
                    """,
                    tenant_id,
                )
        except Exception as e:
            logger.error(f"Error deleting all documents: {e}")


class PGVectorDocumentChunkRepository(DocumentChunkRepository):
    """Manages document chunks in a PostgreSQL database with pgvector."""

    def __init__(self):
        """Initialize repository."""
        pass

    async def get_all(self, tenant_id: str) -> list[dict]:
        """Get all document chunks for a specific tenant."""
        async with PGVectorDatabase.get_connection() as connection:
            results = await connection.fetch(
                """
                SELECT id,
                       tenant_id,
                       fk_document_id,
                       type,
                       chunk,
                       page_number,
                       embedding,
                       created_at,
                       updated_at
                FROM document_chunk
                WHERE tenant_id = $1
                """,
                tenant_id,
            )
            return [
                DocumentChunk(
                    id=result["id"],
                    tenant_id=result["tenant_id"],
                    document_id=result["fk_document_id"],
                    type=result["type"],
                    chunk=result["chunk"],
                    page_number=result["page_number"],
                    embedding=result["embedding"] or [],
                    created_at=result["created_at"],
                    updated_at=result["updated_at"],
                )
                for result in results
            ]

    async def get_by_id(self, tenant_id: str, document_chunk_id: str):
        """Get document chunk by ID."""
        async with PGVectorDatabase.get_connection() as connection:
            result = await connection.fetchrow(
                """
                SELECT id,
                       tenant_id,
                       fk_document_id,
                       type,
                       chunk,
                       page_number,
                       embedding,
                       created_at,
                       updated_at
                FROM document_chunk
                WHERE id = $1 AND tenant_id = $2
                """,
                document_chunk_id,
                tenant_id,
            )
            if result is None:
                return None
            return DocumentChunk(
                id=result["id"],
                tenant_id=result["tenant_id"],
                document_id=result["fk_document_id"],
                type=result["type"],
                chunk=result["chunk"],
                page_number=result["page_number"],
                embedding=result["embedding"] or [],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )

    async def insert(self, tenant_id: str, chunks: DocumentChunk):
        """Insert document chunk into database."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        INSERT INTO document_chunk (id, tenant_id, fk_document_id, type, chunk, page_number, embedding)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        chunks.id,
                        tenant_id,
                        chunks.document_id,
                        chunks.type,
                        chunks.chunk,
                        chunks.page_number,
                        chunks.embedding or [],
                    )
        except Exception as e:
            logger.error(f"Error inserting document chunk: {e}")

    async def update(self, tenant_id: str, chunk: DocumentChunk):
        """Update document chunk by ID."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        UPDATE document_chunk
                        SET type = $1, chunk = $2, page_number = $3, embedding = $4, updated_at = NOW()
                        WHERE id = $5 AND tenant_id = $6
                        """,
                        chunk.type,
                        chunk.chunk,
                        chunk.page_number,
                        chunk.embedding or [],
                        chunk.id,
                        tenant_id,
                    )
        except Exception as e:
            logger.error(f"Error updating document chunk: {e}")

    async def delete(self, tenant_id: str, document_chunk_id: str):
        """Delete document chunk by ID."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        DELETE FROM document_chunk
                        WHERE id = $1 AND tenant_id = $2
                        """,
                        document_chunk_id,
                        tenant_id,
                    )
        except Exception as e:
            logger.error(f"Error deleting document chunk: {e}")

    async def delete_all(self, tenant_id: str):
        """Delete all records associated with a specific tenant ID."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        DELETE FROM document_chunk
                        WHERE tenant_id = $1
                        """,
                        tenant_id,
                    )
        except Exception as e:
            logger.error(f"Error deleting all document chunks: {e}")

    async def get_by_document_id(self, tenant_id: str, document_id: str):
        """Get document chunks by document ID."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                result = await connection.fetch(
                    """
                    SELECT * FROM document_chunk
                    WHERE tenant_id = $1 AND fk_document_id = $2
                    """,
                    tenant_id,
                    document_id,
                )
                return [
                    DocumentChunk(
                        id=record["id"],
                        tenant_id=record["tenant_id"],
                        document_id=record["fk_document_id"],
                        type=record["type"],
                        chunk=record["chunk"],
                        page_number=record["page_number"],
                        embedding=record["embedding"] or [],
                        created_at=record["created_at"],
                        updated_at=record["updated_at"],
                    )
                    for record in result
                ]
        except Exception as e:
            logger.error(f"Error getting document chunks by document ID: {e}")
            return []

    async def search_by_similarity(self, tenant_id: str, vector: list[float], similarity_threshold: float = 0.8, limit: int = 100):
        """Search for document chunks similar to a given vector."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                result = await connection.fetch(
                    """
                    SELECT * FROM document_chunk
                    WHERE tenant_id = $1 AND embedding <-> $2 < $3
                    limit $4
                    """,
                    tenant_id,
                    vector,
                    similarity_threshold,
                    limit,
                )
                return [
                    DocumentChunk(
                        id=record["id"],
                        tenant_id=record["tenant_id"],
                        document_id=record["fk_document_id"],
                        type=record["type"],
                        chunk=record["chunk"],
                        page_number=record["page_number"],
                        embedding=record["embedding"] or [],
                        created_at=record["created_at"],
                        updated_at=record["updated_at"],
                    )
                    for record in result
                ]
        except Exception as e:
            logger.error(f"Error searching document chunks by similarity: {e}")
            return []

    async def search_by_similarity_on_specific_documents(self, tenant_id: str, vector: list[float], document_ids: list[str], similarity_threshold: float, limit: int):
        """Search for document chunks similar to a given vector within specific documents."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                result = await connection.fetch(
                    """
                    SELECT * FROM document_chunk
                    WHERE tenant_id = $1 AND fk_document_id = ANY($2) AND embedding <-> $3 < $4
                    LIMIT $5
                    """,
                    tenant_id,
                    document_ids,
                    vector,
                    similarity_threshold,
                    limit,
                )
                return [
                    DocumentChunk(
                        id=record["id"],
                        tenant_id=record["tenant_id"],
                        document_id=record["fk_document_id"],
                        type=record["type"],
                        chunk=record["chunk"],
                        page_number=record["page_number"],
                        embedding=record["embedding"] or [],
                        created_at=record["created_at"],
                        updated_at=record["updated_at"],
                    )
                    for record in result
                ]
        except Exception as e:
            logger.error(f"Error searching document chunks by similarity on specific documents: {e}")
            return []

    async def insert_batch(self, tenant_id: str, items: list[DocumentChunk]):
        """Insert multiple document chunks into the database using asyncpg executemany."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.executemany(
                        """
                        INSERT INTO document_chunk (id, tenant_id, fk_document_id, type, chunk, page_number, embedding)
                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        [
                            (
                                chunk.id,
                                tenant_id,
                                chunk.document_id,
                                chunk.type,
                                chunk.chunk,
                                chunk.page_number,
                                chunk.embedding if chunk.embedding is not None else [],
                            )
                            for chunk in items
                        ],
                    )
        except Exception as e:
            logger.error(f"Error inserting batch of document chunks: {e}")


class PGVectorQueryRepository(QueryRepository):
    def __init__(self):
        """Initialize repository."""
        pass

    async def get_all(self, tenant_id: str) -> list[dict]:
        """Get all records associated with a specific tenant ID."""
        pass

    async def get_by_id(self, tenant_id: str, query_id: str):
        """Get a record by its ID."""
        pass

    async def create(self, tenant_id: str, query: list[Query]):
        """Create a new record in the repository."""
        pass

    async def update(self, tenant_id: str, query: Query):
        """Update an existing record in the repository."""
        pass

    async def delete(self, tenant_id: str, query_id: str):
        """Delete a record from the repository."""
        pass

    async def delete_all(self, tenant_id: str):
        """Delete all records associated with a specific tenant ID."""
        pass

    async def get_related_chunks(self, tenant_id, query_id, limit: int = 100):
        """Get chunks related to a specific query."""
        pass
