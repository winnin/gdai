from abc import ABC, abstractmethod

from .models import ChunkModel, DocumentModel, QueryModel


class BaseRepository(ABC):
    """A base class for repositories.

    This class defines the basic structure and methods that all repositories should implement.
    """

    def __init__(self):
        """Initialize the base repository."""
        pass

    @abstractmethod
    async def get_all_documents(self, tenant_id: str) -> list[DocumentModel]:
        """Retrieve all documents for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose documents to retrieve.

        Returns:
            list[DocumentModel]: List of document models belonging to the tenant.

        Raises:
            ValueError: If there's an error retrieving the documents.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def insert_document(self, document: DocumentModel) -> None:
        """Insert a new document into the database.

        Args:
            document: The document model to insert.

        Raises:
            ValueError: If there's an error inserting the document.
        """
        pass

    @abstractmethod
    async def delete_document(self, tenant_id: str, document_id: str) -> None:
        """Delete a specific document by ID for a tenant.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document to delete.

        Raises:
            ValueError: If there's an error deleting the document.
        """
        pass

    @abstractmethod
    async def insert_chunks(self, chunks: list[ChunkModel]) -> None:
        """Insert multiple chunks into the database in batches.

        Args:
            chunks: List of chunk models to insert.

        Raises:
            ValueError: If there's an error inserting the chunks.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    async def delete_chunks(self, tenant_id: str, document_id: str) -> None:
        """Delete all chunks for a specific document of a tenant.

        Args:
            tenant_id: The ID of the tenant.
            document_id: The ID of the document whose chunks to delete.

        Raises:
            ValueError: If there's an error deleting the chunks.
        """
        pass

    @abstractmethod
    async def insert_query(self, query: QueryModel) -> None:
        """Insert a new query into the database.

        Args:
            query: The query model to insert.

        Raises:
            ValueError: If there's an error inserting the query.
        """
        pass

    @abstractmethod
    async def search_chunks_by_similarity(
        self, tenant_id: str, query_id: str, query_vector: list[float], similarity_threshold: float, limit: int = 10
    ) -> list[tuple[ChunkModel, float]]:
        """Search for chunks by vector similarity across all documents for a tenant.

        Args:
            tenant_id: The ID of the tenant to search within.
            query_id: The ID of the query being performed.
            query_vector: The embedding vector to compare against chunks.
            similarity_threshold: The minimum similarity score (0-1) for returned results.
            limit: The maximum number of results to return.

        Returns:
            list[tuple[ChunkModel, float]]: List of tuples containing chunks and their similarity scores.

        Raises:
            ValueError: If no chunks meet the similarity threshold or there's an error.
        """
        pass

    @abstractmethod
    async def search_chunks_by_similarity_and_document_ids(
        self,
        tenant_id: str,
        query_id: str,
        query_vector: list[float],
        document_ids: list[str],
        similarity_threshold: float,
        limit: int = 10,
    ) -> list[tuple[ChunkModel, float]]:
        """Search for chunks by vector similarity within specific documents.

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
        pass

    @abstractmethod
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
        pass
