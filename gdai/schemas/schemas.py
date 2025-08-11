import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum, DocumentTypeEnum, QueryStatusEnum, SimilarityTypeEnum


class BaseSchema(BaseModel):
    id: UUID | None = None
    tenant_id: str = Field(min_length=1)
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now())


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


class Query(BaseSchema):
    query: str = ""
    result: str = ""
    status: QueryStatusEnum = QueryStatusEnum.pending
    similarity: SimilarityTypeEnum = SimilarityTypeEnum.cosine
    result_chunks: list["ResultChunk"] | None = []


class RawDocument(BaseModel):
    name: str = Field(min_length=1)
    path: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    type: DocumentTypeEnum
    texts: list[tuple[int, str]] | None = None  # List of tuples (page_number, text)
    tables: list[tuple[int, str]] | None = None  # List of tuples (page_number, table_data)
    images: list[tuple[int, str]] | None = None  # List of tuples (page_number, image_data)


class ResultChunk(BaseModel):
    chunk: str
    type: ChunkTypeEnum
    document_id: str
    page_number: int
    similarity_score: float = 0.0


class QueryResult(BaseModel):
    query: str
    result: str
    status: QueryStatusEnum
    result_chunks: list[ResultChunk] | None = []
