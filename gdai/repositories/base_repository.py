from abc import ABC, abstractmethod

from gdai.schemas import Chunk, Document


class BaseRepository(ABC):
    """A base class for repositories.

    This class defines the basic structure and methods that all repositories should implement.
    """

    def __init__(self):
        """Initialize the base repository."""
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
    async def get_document_chunks(self, tenant_id: str, document_id: str) -> list[Document]:
        """Get all chunks for a specific document.

        Args:
            tenant_id: The ID of the tenant
            document_id: The ID of the document

        Returns:
            list[Document]: The list of document chunks
        """
        pass

    @abstractmethod
    async def update_document(self, document: Document) -> Document:
        """Update a document in the database.

        Args:
            document: The Document model to update

        Returns:
            Document: The updated document
        """
        pass

    @abstractmethod
    async def update_chunks(self, chunks: list[Document]) -> list[Chunk]:
        """Update chunks in the database.

        Args:
            chunks: A list of Document models to update

        Returns:
            list[Chunk]: The updated chunks
        """
        pass

    @abstractmethod
    async def insert_document_and_chunks(self, document: Document) -> Document:
        """Insert a document and its associated chunks into the database.

        Args:
            document: The Document model to insert

        Returns:
            Document: The inserted document with updated IDs
        """
        pass

    @abstractmethod
    async def delete_document_and_chunks(self, document_id: str) -> bool:
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
