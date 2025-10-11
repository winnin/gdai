"""Document domain models."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from gdai.commons.enums import DocumentStatusEnum, DocumentTypeEnum


class DocumentCreateDTO(BaseModel):
    """DTO for creating a new document."""

    name: str = Field(..., description="Document name", min_length=1, max_length=255)
    type: DocumentTypeEnum = Field(..., description="Document type (pdf, docx, txt, etc)")
    chunk_strategy: str | None = Field(None, description="Chunking strategy to use")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "contract.pdf",
                "type": "pdf",
                "chunk_strategy": "recursive",
            }
        }


class DocumentDTO(BaseModel):
    """DTO for document representation."""

    id: UUID = Field(..., description="Document unique identifier")
    tenant_id: str = Field(..., description="Tenant identifier")
    name: str = Field(..., description="Document name")
    status: DocumentStatusEnum = Field(..., description="Processing status")
    type: DocumentTypeEnum = Field(..., description="Document type")
    chunk_strategy: str | None = Field(None, description="Chunking strategy used")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "tenant123",
                "name": "contract.pdf",
                "status": "processed",
                "type": "pdf",
                "chunk_strategy": "recursive",
                "created_at": "2025-01-15T10:30:00Z",
                "updated_at": "2025-01-15T10:35:00Z",
            }
        }


class DocumentStatusDTO(BaseModel):
    """DTO for document status information."""

    id: UUID = Field(..., description="Document unique identifier")
    status: DocumentStatusEnum = Field(..., description="Processing status")
    chunk_count: int | None = Field(None, description="Number of chunks extracted")
    error_message: str | None = Field(None, description="Error message if processing failed")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "processed",
                "chunk_count": 42,
                "error_message": None,
            }
        }


class DocumentListResponse(BaseModel):
    """Response for listing documents."""

    documents: list[DocumentDTO] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")

    class Config:
        json_schema_extra = {
            "example": {
                "documents": [
                    {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "tenant_id": "tenant123",
                        "name": "contract.pdf",
                        "status": "processed",
                        "type": "pdf",
                        "chunk_strategy": "recursive",
                        "created_at": "2025-01-15T10:30:00Z",
                        "updated_at": "2025-01-15T10:35:00Z",
                    }
                ],
                "total": 1,
            }
        }
