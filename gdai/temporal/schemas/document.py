from uuid import UUID

from pydantic import BaseModel, Field

from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum, DocumentTypeEnum

from .base import BaseSchema


class Document(BaseSchema):
    name: str = ""
    status: DocumentStatusEnum = DocumentStatusEnum.uploaded
    type: DocumentTypeEnum = DocumentTypeEnum.pdf
    chunk_strategy: str
    chunks: list["Chunk"] | None = []
    retry_extraction: int = 0
    retry_embedding: int = 0


class Chunk(BaseSchema):
    type: ChunkTypeEnum
    chunk: str = ""
    page_number: int
    embedding: list[float] | None = None
    document_id: UUID | None = None


class RawDocument(BaseModel):
    name: str = Field(min_length=1)
    path: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    type: DocumentTypeEnum
    texts: list[tuple[int, str]] | None = None  # List of tuples (page_number, text)
    tables: list[tuple[int, str]] | None = None  # List of tuples (page_number, table_data)
    images: list[tuple[int, str]] | None = None  # List of tuples (page_number, image_data)
