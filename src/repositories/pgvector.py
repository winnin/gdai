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
        """Get all records associated with a specific tenant ID."""
        pass

    async def get_by_id(self, tenant_id: str, document_chunk_id: str):
        """Get a record by its ID."""
        pass

    async def create(self, tenant_id: str, chunks: list[DocumentChunk]):
        """Create a new record in the repository."""
        pass

    async def update(self, tenant_id: str, chunk: DocumentChunk):
        """Update an existing record in the repository."""
        pass

    async def delete(self, tenant_id: str, document_chunk_id: str):
        """Delete a record from the repository."""
        pass

    async def delete_all(self, tenant_id: str):
        """Delete all records associated with a specific tenant ID."""
        pass

    async def get_by_document_id(self, tenant_id: str, document_id: str):
        pass

    async def search_by_similarity(self, tenant_id, vector, limit=100):
        pass


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
