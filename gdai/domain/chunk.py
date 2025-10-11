"""Chunk domain models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from gdai.commons.enums import ChunkTypeEnum


class ChunkDTO(BaseModel):
    """DTO for chunk representation."""

    id: UUID = Field(..., description="Chunk unique identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    document_id: UUID = Field(..., description="Parent document ID")
    type: ChunkTypeEnum = Field(..., description="Chunk type")
    chunk: str = Field(..., description="Chunk text content")
    page_number: int | None = Field(None, description="Page number in source document")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "tenant123",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "type": "text",
                "chunk": "This is a sample text chunk from the document.",
                "page_number": 1,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:35:00Z",
            }
        }


class ChunkWithEmbeddingDTO(ChunkDTO):
    """DTO for chunk with embedding vector."""

    embedding: list[float] | None = Field(None, description="Embedding vector")
    similarity_score: float | None = Field(None, description="Similarity score (for search results)")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "tenant123",
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "type": "text",
                "chunk": "This is a sample text chunk from the document.",
                "page_number": 1,
                "embedding": [0.1, 0.2, 0.3],  # Truncated for example
                "similarity_score": 0.95,
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:35:00Z",
            }
        }


class ChunkListResponse(BaseModel):
    """Response for listing chunks."""

    chunks: list[ChunkDTO] = Field(..., description="List of chunks")
    total: int = Field(..., description="Total number of chunks")
    document_id: UUID = Field(..., description="Parent document ID")

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "550e8400-e29b-41d4-a716-446655440000",
                "chunks": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440000",
                        "tenant_id": "tenant123",
                        "document_id": "550e8400-e29b-41d4-a716-446655440000",
                        "type": "text",
                        "chunk": "This is a sample text chunk.",
                        "page_number": 1,
                        "created_at": "2025-01-15T10:30:00Z",
                        "updated_at": "2025-01-15T10:35:00Z",
                    }
                ],
                "total": 1,
            }
        }
