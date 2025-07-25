from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """A base class for repositories.

    This class defines the basic structure and methods that all repositories should implement.
    """

    @abstractmethod
    async def get_all(self, tenant_id: str, *args, **kwargs) -> list[dict]:
        """Get all records associated with a specific tenant ID."""
        pass

    @abstractmethod
    async def get_by_id(self, tenant_id: str, id: str, *args, **kwargs):
        """Get a record by its ID."""
        pass

    @abstractmethod
    async def insert(self, tenant_id: str, *args, **kwargs):
        """Create a new record in the repository."""
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
    async def delete_all(self, tenant_id: str, *args, **kwargs):
        """Delete all records associated with a specific tenant ID."""
        pass


class DocumentRepository(BaseRepository):
    """A repository for managing documents.

    This class extends BaseRepository and implements methods specific to document management.
    """

    pass


class ChunkRepository(BaseRepository):
    """A repository for managing document chunks.

    This class extends BaseRepository and implements methods specific to document chunk management.
    """

    @abstractmethod
    async def get_by_document_id(self, tenant_id: str, document_id: str, *args, **kwargs):
        """Get all chunks associated with a specific document ID."""
        pass

    @abstractmethod
    async def search_by_similarity(
        self, tenant_id: str, vector: list[float], similarity_threshold: float, limit: int, *args, **kwargs
    ):
        """Search for chunks similar to a given vector."""
        pass

    @abstractmethod
    async def search_by_similarity_on_specific_documents(
        self,
        tenant_id: str,
        vector: list[float],
        document_ids: list[str],
        similarity_threshold: float,
        limit: int,
        *args,
        **kwargs,
    ):
        """Search for chunks similar to a given vector within specific documents."""
        pass

    @abstractmethod
    async def insert_batch(self, tenant_id: str, items: list):
        """Insert multiple records in the repository."""
        pass

    @abstractmethod
    async def update_batch(self, tenant_id: str, items: list, *args, **kwargs):
        """Update an existing record in the repository."""
        pass


class QueryRepository(BaseRepository):
    """A repository for managing query-related operations.

    This class extends BaseRepository and implements methods specific to search functionality.
    """

    async def get_related_chunks(self, tenant_id: str, query_id: str, limit: int, *args, **kwargs):
        """Get chunks related to a specific query."""
        pass
