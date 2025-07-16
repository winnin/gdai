from pydantic import BaseModel, Field

from src.schemas.chunk import DocumentChunk


class QueryDocumentChunk(DocumentChunk):
    """
    Represents a document chunk with additional fields for user queries.
    Attributes:
        similarity: Similarity score between the query and the chunk.
        similarity_type: Type of similarity metric used (e.g., cosine, dot_product).
    """

    similarity: float = Field(default=0.0)
    similarity_type: str = Field(default="cosine", description="Type of similarity metric used (e.g., cosine, dot_product).")


class Query(BaseModel):
    """Represents a  query for searching document chunks.
    Attributes:
        id: Unique identifier for the query (optional).
        tenant_id: Identifier for the tenant context of the query.
        query: The search query text (1-1000 characters).
        result: The result of the query (optional).
        status: Status of the query (default: "pending").
        num_chunks: Number of relevant chunks to retrieve (1-1000).
        created_at: Timestamp when the query was created (optional).
        updated_at: Timestamp when the query was last updated (optional).
        chunks: List of document chunks related to this query.
    """

    id: str | None = Field(default=None)
    tenant_id: str
    query: str = Field(min_length=1, max_length=1000)
    result: str | None = Field(default=None)
    status: str = Field(default="pending")
    created_at: str | None = Field(default=None)
    updated_at: str | None = Field(default=None)
    chunks: list[QueryDocumentChunk] = Field(default_factory=list)
