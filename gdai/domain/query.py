"""Query domain models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from gdai.commons.enums import QueryStatusEnum


class QueryCreateDTO(BaseModel):
    """DTO for creating a new query."""

    query: str = Field(..., description="Query text", min_length=1)
    document_ids: list[UUID] | None = Field(
        None, description="List of document IDs to search within (optional, searches all if not provided)"
    )
    similarity_threshold: float = Field(0.7, description="Minimum similarity threshold", ge=0.0, le=1.0)
    limit: int = Field(5, description="Maximum number of chunks to retrieve", ge=1, le=100)

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is the main purpose of this contract?",
                "document_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                "similarity_threshold": 0.7,
                "limit": 5,
            }
        }


class QueryDTO(BaseModel):
    """DTO for query representation."""

    id: UUID = Field(..., description="Query unique identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    query: str = Field(..., description="Query text")
    result: str | None = Field(None, description="Generated result")
    status: QueryStatusEnum = Field(..., description="Query processing status")
    similarity: str = Field("cosine", description="Similarity metric used")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "tenant123",
                "query": "What is the main purpose of this contract?",
                "result": "The main purpose of this contract is to establish...",
                "status": "completed",
                "similarity": "cosine",
                "created_at": "2025-01-15T10:40:00Z",
                "updated_at": "2025-01-15T10:40:30Z",
            }
        }


class QueryResultDTO(BaseModel):
    """DTO for query result with relevant chunks."""

    query_id: UUID = Field(..., description="Query unique identifier")
    query_text: str = Field(..., description="Original query text")
    result: str = Field(..., description="Generated answer")
    status: QueryStatusEnum = Field(..., description="Query processing status")
    relevant_chunks: list[dict] = Field(..., description="Relevant chunks with similarity scores")
    processing_time_ms: int | None = Field(None, description="Processing time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "770e8400-e29b-41d4-a716-446655440000",
                "query_text": "What is the main purpose of this contract?",
                "result": "The main purpose of this contract is to establish...",
                "status": "completed",
                "relevant_chunks": [
                    {
                        "chunk_id": "660e8400-e29b-41d4-a716-446655440000",
                        "content": "This contract establishes...",
                        "similarity_score": 0.95,
                        "page_number": 1,
                    }
                ],
                "processing_time_ms": 1250,
            }
        }


class QueryListResponse(BaseModel):
    """Response for listing queries."""

    queries: list[QueryDTO] = Field(..., description="List of queries")
    total: int = Field(..., description="Total number of queries")

    class Config:
        json_schema_extra = {
            "example": {
                "queries": [
                    {
                        "id": "770e8400-e29b-41d4-a716-446655440000",
                        "tenant_id": "tenant123",
                        "query": "What is the main purpose?",
                        "result": "The main purpose is...",
                        "status": "completed",
                        "similarity": "cosine",
                        "created_at": "2025-01-15T10:40:00Z",
                        "updated_at": "2025-01-15T10:40:30Z",
                    }
                ],
                "total": 1,
            }
        }
