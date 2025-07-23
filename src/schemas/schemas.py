import datetime
import enum
from uuid import UUID

from pydantic import BaseModel, Field


class DocumentStatusEnum(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class DocumentTypeEnum(str, enum.Enum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"


class ChunkTypeEnum(str, enum.Enum):
    paragraph = "paragraph"
    size = "size"
    image = "image"
    table = "table"


class QueryStatusEnum(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class SimilarityTypeEnum(str, enum.Enum):
    cosine = "cosine"
    euclidean = "euclidean"


class BaseSchema(BaseModel):
    id: UUID | None = None
    tenant_id: str = Field(min_length=1)
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))


class Document(BaseSchema):
    name: str = ""
    status: DocumentStatusEnum = DocumentStatusEnum.uploaded
    type: DocumentTypeEnum = DocumentTypeEnum.pdf
    chunks: list["Chunk"] | None = []


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
    query_chunks: list["QueryChunkLink"] | None = []


class QueryChunkLink(BaseModel):
    query_id: UUID
    chunk_id: UUID
    similarity_score: float = 0.0
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
