"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

from src.shared.database import PGVectorDatabase
from src.shared.logger import logger
from src.shared.schema import Document, DocumentChunk


class DocumentRepository:
    """
    Manages documents and chunks in a PostgreSQL database with pgvector.
    """

    def __init__(self):
        """
        Initialize repository.
        """

    async def get_document_by_id(self, document_id: str):
        """
        Get document by ID.

        Args:
            document_id (str): The ID of the document.
        Returns:
            Document: The document object or None if not found.
        """
        async with PGVectorDatabase.get_connection() as connection:
            result = await connection.fetchrow(
                """SELECT id,
                          name,
                          tenant_id,
                          pages,
                          embedding_model_name
                    FROM document
                    WHERE id = $1""",
                document_id,
            )
            if result is None:
                return None
            doc = Document(
                doc_id=result["id"],
                tenant_id=result["tenant_id"],
                doc_name=result["name"],
                pages=result["pages"],
                embedding_model_name=result["embedding_model_name"],
            )
            return doc

    async def get_document_chunk_by_id(self, chunk_id: str):
        """
        Get document chunk by ID.

        Args:
            chunk_id (str): The ID of the chunk.
        Returns:
            DocumentChunk: The document chunk object or None if not found.
        """
        async with PGVectorDatabase.get_connection() as connection:
            result = await connection.fetchrow(
                """SELECT id,
                              tenant_id,
                              chunk_text,
                              page_number,
                              begin_offset,
                              end_offset,
                              embedding,
                              fk_doc_id
                    FROM document_chunk
                    WHERE id = $1""",
                chunk_id,
            )

            if result is None:
                return None
            doc_chunk = DocumentChunk(
                chunk_id=result["id"],
                tenant_id=result["tenant_id"],
                chunk_text=result["chunk_text"],
                page_number=result["page_number"],
                begin_offset=result["begin_offset"],
                end_offset=result["end_offset"],
                embedding=result["embedding"],
                doc_id=result["fk_doc_id"],
            )
        return doc_chunk

    async def insert_document(self, document, document_chunks):
        """
        Insert document and chunks into database.

        Args:
            document (Document): The document to insert.
            document_chunks (List[DocumentChunk]): The chunks to insert.
        Returns:
            None
        """
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        INSERT INTO document (id, tenant_id, name)
                        VALUES ($1, $2, $3)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        document.doc_id,
                        document.tenant_id,
                        document.doc_name,
                    )

                    for chunk in document_chunks:
                        await connection.execute(
                            """
                            INSERT INTO document_chunk (id, chunk_text, page_number, begin_offset, end_offset, embedding, fk_doc_id, tenant_id)
                            VALUES ($1, $2, $3, $4, $5, $6::vector, $7, $8)
                            ON CONFLICT (id) DO NOTHING;
                            """,
                            chunk.chunk_id,
                            chunk.chunk_text,
                            chunk.page_number,
                            chunk.begin_offset,
                            chunk.end_offset,
                            chunk.embedding,
                            chunk.doc_id,
                            chunk.tenant_id,
                        )

        except Exception as e:
            logger.error(f"Error inserting document: {e}")

    async def delete_document(self, document_id: str):
        """Delete document by ID."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        "DELETE FROM document_chunk WHERE fk_doc_id = $1", document_id
                    )
                    await connection.execute(
                        "DELETE FROM document WHERE id = $1", document_id
                    )
        except Exception as e:
            print(f"Error deleting document: {e}")

    async def clean_tenant_database(self, tenant_id: str):
        """Delete all documents and chunks for a tenant."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        "DELETE FROM document_chunk where tenant_id = $1", tenant_id
                    )
                    await connection.execute(
                        "DELETE FROM document where tenant_id = $1", tenant_id
                    )
        except Exception as e:
            print(f"Error cleaning tenant database: {e}")
