from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """A base class for repositories.

    This class defines the basic structure and methods that all repositories should implement.
    """

    @abstractmethod
    async def create(self, tenant_id: str, *args, **kwargs):
        """Create a new record in the repository."""
        pass

    @abstractmethod
    async def read(self, tenant_id: str, *args, **kwargs):
        """Read a record from the repository."""
        pass

    @abstractmethod
    async def update(self, tenant_id: str, *args, **kwargs):
        """Update an existing record in the repository."""
        pass

    @abstractmethod
    async def delete(self, tenant_id: str, *args, **kwargs):
        """Delete a record from the repository."""
        pass

    @abstractmethod
    async def delete_many(self, tenant_id: str, filter_criteria, *args, **kwargs):
        """Delete multiple records based on filter criteria."""
        pass

    @abstractmethod
    async def get_by_id(self, tenant_id: str, id: str, *args, **kwargs):
        """Get a record by its ID."""
        pass


class DocumentRepository(BaseRepository):
    """A repository for managing documents.

    This class extends BaseRepository and implements methods specific to document management.
    """

    @abstractmethod
    async def get_all_documents_by_tenant_id(self, tenant_id: str, *args, **kwargs) -> list[dict]:
        """Get all documents associated with a specific tenant ID."""
        pass


class ChunkRepository(BaseRepository):
    """A repository for managing document chunks.

    This class extends BaseRepository and implements methods specific to document chunk management.
    """

    async def get_by_document_id(self, tenant_id: str, document_id: str, *args, **kwargs):
        """Get all chunks associated with a specific document ID."""
        pass

    async def get_by_tenant_id(self, tenant_id: str, *args, **kwargs):
        """Get all chunks associated with a specific tenant ID."""
        pass

    async def search_by_similarity(self, tenant_id: str, vector, limit: int, *args, **kwargs):
        """Search for chunks similar to a given vector."""
        pass


class QueryRepository(BaseRepository):
    """A repository for managing query-related operations.

    This class extends BaseRepository and implements methods specific to search functionality.
    """

    async def get_query_related_chunks(self, tenant_id: str, query_id: str, limit: int, *args, **kwargs):
        """Get chunks related to a specific query."""
        pass
