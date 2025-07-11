"""Repository for managing documents and chunks in PostgreSQL with pgvector."""

from __future__ import annotations

from src.config.database import PGVectorDatabase
from src.config.logger import logger
from src.repositories.base import DocumentRepository
from src.schemas.chunk import DocumentChunk
from src.schemas.document import Document


class PGVectorDocumentRepository(DocumentRepository):
    """Manages documents and chunks in a PostgreSQL database with pgvector."""

    def __init__(self):
        """Initialize repository."""

    async def get_all_documents_by_tenant_id(self, tenant_id: str):
        """Get all documents for a specific tenant."""
        async with PGVectorDatabase.get_connection() as connection:
            results = await connection.fetch(
                """
                SELECT id,
                       tenant_id,
                       name,
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
                type=result["type"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
            return doc

    async def get_document_chunk_by_id(self, tenant_id: str, chunk_id: str):
        """Get document chunk by ID."""
        async with PGVectorDatabase.get_connection() as connection:
            result = await connection.fetchrow(
                """
                SELECT id,
                       tenant_id,
                       chunk_type,
                       chunk_text,
                       page_number,
                       embedding,
                       fk_document_id,
                       created_at,
                       updated_at
                FROM document_chunk
                WHERE id = $1 AND tenant_id = $2
                """,
                chunk_id,
                tenant_id,
            )
            if result is None:
                return None
            doc_chunk = DocumentChunk(
                id=result["id"],
                tenant_id=result["tenant_id"],
                chunk_type=result["chunk_type"],
                chunk=result["chunk_text"],
                page_number=result["page_number"],
                embedding=result["embedding"],
                document_id=result["fk_document_id"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )
            return doc_chunk

    async def create(self, tenant_id: str, document, document_chunks):
        """Insert document and chunks into database."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        """
                        INSERT INTO document (id, tenant_id, name, type)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (id) DO NOTHING;
                        """,
                        document.id,
                        tenant_id,
                        document.name,
                        document.type,
                    )

                    for chunk in document_chunks:
                        await connection.execute(
                            """
                            INSERT INTO document_chunk (
                                id, tenant_id, chunk_type, chunk_text, page_number, embedding, fk_document_id
                            )
                            VALUES ($1, $2, $3, $4, $5, $6::vector, $7)
                            ON CONFLICT (id) DO NOTHING;
                            """,
                            chunk.chunk_id,
                            chunk.tenant_id,
                            chunk.chunk_type,
                            chunk.chunk_text,
                            chunk.page_number,
                            chunk.embedding,
                            chunk.doc_id,
                        )

        except Exception as e:
            logger.error(f"Error inserting document: {e}")

    async def delete(self, tenant_id: str, document_id: str):
        """Delete document by ID."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute(
                        "DELETE FROM document_chunk WHERE fk_document_id = $1 AND tenant_id = $2",
                        document_id,
                        tenant_id,
                    )
                    await connection.execute(
                        "DELETE FROM document WHERE id = $1 AND tenant_id = $2",
                        document_id,
                        tenant_id,
                    )
        except Exception as e:
            logger.error(f"Error deleting document: {e}")

    async def clean_tenant_database(self, tenant_id: str):
        """Delete all documents and chunks for a tenant."""
        try:
            async with PGVectorDatabase.get_connection() as connection:
                async with connection.transaction():
                    await connection.execute("DELETE FROM document_chunk WHERE tenant_id = $1", tenant_id)
                    await connection.execute("DELETE FROM document WHERE tenant_id = $1", tenant_id)
        except Exception as e:
            logger.error(f"Error cleaning tenant database: {e}")

    async def read(self, tenant_id: str, *args, **kwargs):
        """Read a record from the repository."""
        pass

    async def update(self, tenant_id: str, *args, **kwargs):
        """Update an existing record in the repository."""
        pass

    async def delete_many(self, tenant_id: str, filter_criteria, *args, **kwargs):
        """Delete multiple records based on filter criteria."""
        pass


# class SearchRepository:
#     """Repository for managing search-related database operations."""

#     def __init__(self):
#         """Initialize repository."""

#     async def create_message_entry(self, tenant_id:str, tenant_id: str, query_id: str, query_text: str) -> str:
#         """Create a new message entry in the database.

#         Args:
#             tenant_id (str): The ID of the tenant.
#             query_id (str): The ID of the query.
#             query_text (str): The text of the query.

#         Returns:
#             id (str): The ID of the newly created message entry.
#         """
#         try:
#             async with PGVectorDatabase.get_connection() as conn:
#                 # Insert a new message with 'pending' status
#                 query = """
#                     INSERT INTO message (tenant_id, query_id, query_text, status)
#                     VALUES ($1, $2, $3, 'pending')
#                     RETURNING id
#                 """
#                 result = await conn.fetchval(query, tenant_id, query_id, query_text)
#                 logger.info(f"Created message entry with ID: {result} for tenant: {tenant_id}, query_id: {query_id}")
#                 return result
#         except Exception as e:
#             logger.error(f"Error creating message entry: {e}")
#             raise

#     async def get_chunks_by_vector_similarity(self, tenant_id:str, tenant_id: str, query_id: str, query_embedding: list[float], limit: int) -> list[ChunkQueryResult]:
#         """Get document chunks by vector similarity.

#         Args:
#             tenant_id (str): The ID of the tenant.
#             query_id (str): The ID of the query.
#             query_embedding (List[float]): The embedding vector of the query.
#             limit (int): The maximum number of chunks to return.

#         Returns:
#             List[ChunkQueryResult]: A list of document chunks sorted by similarity.
#         """
#         try:
#             async with PGVectorDatabase.get_connection() as conn:
#                 query = """
#                     SELECT dc.id as chunk_id,
#                            dc.tenant_id as tenant_id,
#                            dc.chunk_text as chunk_text,
#                            dc.page_number as page_number,
#                            dc.begin_offset as begin_offset,
#                            dc.end_offset as end_offset,
#                            dc.fk_doc_id as doc_id,
#                            dc.embedding <-> $2 as similarity_score,
#                            d.name as doc_name
#                     FROM document_chunk dc
#                          INNER JOIN document d ON dc.fk_doc_id = d.id
#                     WHERE dc.tenant_id = $1
#                     ORDER BY dc.embedding <-> $2
#                     LIMIT $3
#                 """

#                 rows = await conn.fetch(query, tenant_id, query_embedding, limit)
#                 result = []
#                 for row in rows:
#                     chunk = DocumentChunk(
#                         tenant_id=row["tenant_id"],
#                         chunk_id=row["chunk_id"],
#                         doc_id=row["doc_id"],
#                         doc_name=row["doc_name"],
#                         chunk_text=row["chunk_text"],
#                         page_number=row["page_number"],
#                         begin_offset=row["begin_offset"],
#                         end_offset=row["end_offset"],
#                     )

#                     chunk_result = ChunkQueryResult(
#                         tenant_id=row["tenant_id"],
#                         query_id=query_id,
#                         chunk=chunk,
#                         similarity=row["similarity_score"],
#                     )
#                     result.append(chunk_result)
#                 return result
#         except Exception as e:
#             logger.error(f"Error fetching chunks by vector similarity: {e}")
#             raise

#     async def update_message_status(self, tenant_id:str, message_id: str, status: str) -> None:
#         """Update the status of a message.

#         Args:
#             message_id (str): The ID of the message to update.
#             status (str): The new status to set for the message.

#         Returns:
#             None
#         """
#         try:
#             async with PGVectorDatabase.get_connection() as conn:
#                 query = "UPDATE message SET status = $1 WHERE id = $2"
#                 await conn.execute(query, status, message_id)
#                 logger.info(f"Updated message {message_id} status to {status}")
#         except Exception as e:
#             logger.error(f"Error updating message status for {message_id}: {e}")
#             raise

#     async def update_message_text_and_status(self, tenant_id:str, message_id: str, text: str) -> None:
#         """Update the text and status of a message.

#         Args:
#             message_id (str): The ID of the message to update.
#             text (str): The new text to set for the message.

#         Returns:
#             None
#         """
#         try:
#             async with PGVectorDatabase.get_connection() as conn:
#                 query = """
#                     UPDATE message
#                     SET result = $1, status = 'completed'
#                     WHERE id = $2
#                 """
#                 await conn.execute(query, text, message_id)
#                 logger.info(f"Updated message {message_id} text and status to completed")
#         except Exception as e:
#             logger.error(f"Error updating message text for {message_id}: {e}")
#             raise

#     async def add_chunks_to_message(self, tenant_id:str, message_id: str, chunks: list[ChunkQueryResult]) -> None:
#         """Add chunks to a message.

#         Args:
#             message_id (str): The ID of the message to which chunks will be added.
#             chunks (List[ChunkQueryResult]): A list of ChunkQueryResult objects to add.

#         Returns:
#             None
#         """
#         try:
#             async with PGVectorDatabase.get_connection() as conn:
#                 for chunk in chunks:
#                     query = """
#                         INSERT INTO chunk_message (fk_message_id, fk_document_chunk_id)
#                         VALUES ($1, $2)
#                     """

#                     await conn.execute(query, message_id, chunk.chunk.chunk_id)
#                 logger.info(f"Added {len(chunks)} chunks to message ID: {message_id}")
#         except Exception as e:
#             logger.error(f"Error adding chunks to message ID {message_id}: {e}")
#             raise
