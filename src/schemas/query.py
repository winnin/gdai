from pydantic import BaseModel, Field

from src.schemas.chunk import DocumentChunk


class QueryInput(BaseModel):
    """Represents a user query with search parameters.

    Used to structure and validate search parameters submitted by users.

    Attributes:
        tenant_id: Identifier for the tenant context of the query.
        query: The search query text (1-1000 characters).
        num_chunks: Number of relevant chunks to retrieve (1-1000, default: 10).
        temperature: Controls randomness in response generation (0.0-1.0, default: 0.5).
    """

    tenant_id: str
    query: str = Field(min_length=1, max_length=1000)
    num_chunks: int = Field(ge=1, le=1000, default=10)

    def __str__(self) -> str:
        """Return a human-readable string representation of the QueryInput.

        Returns:
            A string displaying the query and parameters.
        """
        return f"QueryInput(query={self.query}, num_chunks={self.num_chunks})"


class ChunkQueryResult(BaseModel):
    """Represents a single chunk result from a search query.

    Stores individual search results with their relevance scores.

    Attributes:
        tenant_id: Identifier for the tenant context.
        query: The search query text that produced this result.
        chunk: The document chunk that matches the query.
        similarity: Similarity score between the query and the chunk.
    """

    tenant_id: str
    query_id: str
    chunk: DocumentChunk
    similarity: float

    def __str__(self) -> str:
        """Return a human-readable string representation of the ChunkQueryResult.

        Returns:
            A string displaying query, chunk ID, and similarity score.
        """
        return f"ChunkQueryResult(query={self.query_id}, chunk_id={self.chunk.chunk_id}, similarity={self.similarity})"


class QueryOutput(BaseModel):
    """Represents the complete response to a query.

    Encapsulates the complete response to a user query, including both
    the generated answer and the supporting evidence chunks.

    Attributes:
        tenant_id: Identifier for the tenant context.
        query: The original search query text.
        answer: Generated answer text based on the query and relevant chunks.
        chunk_result: List of chunks used to generate the answer.
        num_chunks: Number of chunks used in the response (0-1000, default: 0).
        temperature: Temperature value used for answer generation (0.0-1.0, default: 0.5).
    """

    tenant_id: str
    query: str
    answer: str
    chunk_result: list[ChunkQueryResult] = Field(default_factory=list)
    num_chunks: int = Field(ge=0, le=1000, default=0)
    temperature: float = Field(ge=0.0, le=1.0, default=0.5)

    def __str__(self) -> str:
        """Return a human-readable string representation of the QueryOutput.

        Returns:
            A string displaying query, answer, and chunk count.
        """
        return f"QueryOutput(query={self.query}, answer={self.answer}, num_chunks={self.num_chunks})"


class SearchRequest(BaseModel):
    """Request model for search queries."""

    tenant_id: str
    query_id: str
    query_text: str
    chunks_limit: int | None = 100


class SearchResponse(BaseModel):
    """Response model for search queries."""

    message: str
    query_id: str
    status: str
    list_chunks: list | None = None


class ChunkQueryResult(BaseModel):
    """Represents a single chunk result from a search query.

    Stores individual search results with their relevance scores.

    Attributes:
        tenant_id: Identifier for the tenant context.
        query: The search query text that produced this result.
        chunk: The document chunk that matches the query.
        similarity: Similarity score between the query and the chunk.
    """

    tenant_id: str
    query_id: str
    chunk: DocumentChunk
    similarity: float

    def __str__(self) -> str:
        """Return a human-readable string representation of the ChunkQueryResult.

        Returns:
            A string displaying query, chunk ID, and similarity score.
        """
        return f"ChunkQueryResult(query={self.query_id}, chunk_id={self.chunk.chunk_id}, similarity={self.similarity})"


class ChunkQueryResult(BaseModel):
    """Represents a single chunk result from a search query.

    Stores individual search results with their relevance scores.

    Attributes:
        tenant_id: Identifier for the tenant context.
        query: The search query text that produced this result.
        chunk: The document chunk that matches the query.
        similarity: Similarity score between the query and the chunk.
    """

    tenant_id: str
    query_id: str
    chunk: DocumentChunk
    similarity: float

    def __str__(self) -> str:
        """Return a human-readable string representation of the ChunkQueryResult.

        Returns:
            A string displaying query, chunk ID, and similarity score.
        """
        return f"ChunkQueryResult(query={self.query_id}, chunk_id={self.chunk.chunk_id}, similarity={self.similarity})"
