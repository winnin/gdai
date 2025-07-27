from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """A base class for repositories.

    This class defines the basic structure and methods that all repositories should implement.
    """

    def __init__(self):
        """Initialize the base repository."""
        pass

    @abstractmethod
    async def insert_document_and_chunks(self, document):
        """Insert a document and its associated chunks into the database.

        Args:
            document: The Document model to insert

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        pass

    @abstractmethod
    async def remove_tenant_content(self, tenant_id: str) -> bool:
        """Remove all content for a specific tenant.

        Args:
            tenant_id: The ID of the tenant whose content should be removed

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        pass
