"""Schema definitions for document management workflows."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    """Document entity exposed to users."""

    id: str
    name: str
    status: str
    type: str
    chunk_strategy: str | None
    created_at: datetime
    updated_at: datetime


@dataclass
class Chunk:
    """Chunk entity exposed to users."""

    id: str
    document_id: str
    type: str
    chunk: str
    page_number: int | None
    created_at: datetime
    updated_at: datetime


@dataclass
class DocumentStatus:
    """Document status entity."""

    id: str
    status: str
    chunk_count: int
    error_message: str | None = None


@dataclass
class ListDocumentsInput:
    """Input for listing documents."""

    tenant_id: str


@dataclass
class ListDocumentsOutput:
    """Output for listing documents."""

    documents: list[Document]
    total: int


@dataclass
class GetDocumentInput:
    """Input for getting a document."""

    tenant_id: str
    document_id: str


@dataclass
class DeleteDocumentInput:
    """Input for deleting a document."""

    tenant_id: str
    document_id: str


@dataclass
class GetDocumentChunksInput:
    """Input for getting document chunks."""

    tenant_id: str
    document_id: str


@dataclass
class GetDocumentChunksOutput:
    """Output for getting document chunks."""

    document_id: str
    chunks: list[Chunk]
    total: int


@dataclass
class GetDocumentStatusInput:
    """Input for getting document status."""

    tenant_id: str
    document_id: str
