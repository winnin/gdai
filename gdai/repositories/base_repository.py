from abc import ABC, abstractmethod

from gdai.commons.enums import SimilarityTypeEnum
from gdai.schemas import Chunk, Document
from gdai.schemas.schemas import Query


class BaseRepository(ABC):
    """A base class for repositories.

    This class defines the basic structure and methods that all repositories should implement.
    """

    def __init__(self):
        """Initialize the base repository."""
        pass

    @abstractmethod
    async def get_all_documents(self, tenant_id: str) -> list[Document]:
        """Get all documents for a specific tenant.

        Args:
            tenant_id: The ID of the tenant

        Returns:
            list[Document]: A list of Document models
        """
        pass

    @abstractmethod
    async def get_document(self, tenant_id: str, document_id: str) -> Document:
        """Get a document by tenant ID and document ID.

        Args:
            tenant_id: The ID of the tenant
            document_id: The ID of the document
        Returns:
            Document: The retrieved document
        """
        pass

    @abstractmethod
    async def insert_document(self, tenant_id: str, document: Document) -> Document:
        """Insert a new document into the database.

        Args:
            document: The Document model to insert

        Returns:
            Document: The inserted document with updated IDs
        """
        pass

    @abstractmethod
    async def update_document(self, tenant_id: str, document: Document) -> Document:
        """Update a document in the database.

        Args:
            document: The Document model to update

        Returns:
            Document: The updated document
        """
        pass

    @abstractmethod
    async def insert_chunks(self, tenant_id: str, document_id: str, chunks: list[Chunk]) -> list[Chunk]:
        """Insert chunks for a specific document.

        Args:
            tenant_id: The ID of the tenant
            document_id: The ID of the document
            chunks: A list of Chunk models to insert

        Returns:
            list[Chunk]: The inserted chunks with updated IDs
        """
        pass

    @abstractmethod
    async def get_chunks(self, tenant_id: str, document_id: str) -> list[Document]:
        """Get all chunks for a specific document.

        Args:
            tenant_id: The ID of the tenant
            document_id: The ID of the document

        Returns:
            list[Document]: The list of document chunks
        """
        pass

    @abstractmethod
    async def update_chunks(self, tenant_id: str, chunks: list[Document]) -> list[Chunk]:
        """Update chunks in the database.

        Args:
            chunks: A list of Document models to update

        Returns:
            list[Chunk]: The updated chunks
        """
        pass

    @abstractmethod
    async def delete_document_and_chunks(self, tenant_id: str, document_id: str) -> bool:
        """Delete a document and its associated chunks from the database.

        Args:
            document_id: The ID of the document to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete_tenant_content(self, tenant_id: str) -> bool:
        """Remove all content for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose content should be removed
        """
        pass

    @abstractmethod
    async def insert_query(self, tenant_id: str, query: str, similarity: SimilarityTypeEnum) -> str:
        """Insert a query into the database.

        Args:
            tenant_id: The ID of the tenant
            query: The query string to insert

        Returns:
            str: The ID of the inserted query
        """
        pass

    @abstractmethod
    async def search_chunks_by_similarity(self, tenant_id: str, query_vector: list[float], similarity: SimilarityTypeEnum, limit: int = 10) -> list[Chunk]:
        """Search for chunks based on similarity to a query.

        Args:
            tenant_id: The ID of the tenant
            query: The query string to search for
            similarity: The type of similarity to use for the search
            limit: The maximum number of results to return

        Returns:
            list[Chunk]: A list of chunks that match the query
        """
        pass

    @abstractmethod
    async def update_query(self, query_id: str, query: Query) -> None:
        """Update an existing query in the database.

        Args:
            query_id: The ID of the query to update
            query: The new query string
        """
        pass

    @abstractmethod
    async def get_query(self, tenant_id: str, query_id: str) -> Query:
        """Retrieve a query by its ID.

        Args:
            tenant_id: The ID of the tenant
            query_id: The ID of the query to retrieve

        Returns:
            Query: The retrieved query
        """
        pass
