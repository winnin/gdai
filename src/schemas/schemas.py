import datetime
import enum
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable
from sqlmodel import Column, Field, Relationship, SQLModel


class DocumentStatusEnum(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class DocumentTypeEnum(str, enum.Enum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    # Add other types as needed


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


class BaseSchema(SQLModel, table=False):
    id: UUID | None = Field(default=None, primary_key=True)
    tenant_id: str = Field(default="")
    created_at: datetime.datetime = Field(default=datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default=datetime.datetime.now(datetime.timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.datetime.now(datetime.timezone.utc)})


class Document(BaseSchema, table=True):
    __tablename__ = "document"
    name: str = Field(default="")
    status: DocumentStatusEnum = Field(default=DocumentStatusEnum.uploaded)
    type: DocumentTypeEnum = Field(default=DocumentTypeEnum.pdf)

    # Relationships
    chunks: list["Chunk"] = Relationship(back_populates="document", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class Chunk(BaseSchema, table=True):
    __tablename__ = "chunk"
    type: ChunkTypeEnum = Field(nullable=False)
    chunk: str = Field(default="")
    page_number: int = Field()
    embedding: list[float] | None = Field(sa_column=Column(Vector()))

    # Relationships
    document_id: UUID = Field(default=None, foreign_key="document.id")
    document: Document | None = Relationship(back_populates="chunks")

    chunk_queries: list["QueryChunkLink"] = Relationship(back_populates="chunk")


class Query(BaseSchema, table=True):
    __tablename__ = "query"
    query: str = Field(default="")
    result: str = Field(default="")
    status: QueryStatusEnum = Field(default=QueryStatusEnum.pending)
    similarity: SimilarityTypeEnum = Field(default=SimilarityTypeEnum.cosine)

    # Relationships
    query_chunks: list["QueryChunkLink"] = Relationship(back_populates="query")


class QueryChunkLink(SQLModel, table=True):
    __tablename__ = "query_chunk_link"
    query_id: UUID = Field(foreign_key="query.id", primary_key=True)
    chunk_id: UUID = Field(foreign_key="chunk.id", primary_key=True)
    similarity_score: float = Field(default=0.0)
    created_at: datetime.datetime = Field(default=datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.datetime = Field(default=datetime.datetime.now(datetime.timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.datetime.now(datetime.timezone.utc)})

    # Relationships
    query: Query = Relationship(back_populates="query_chunks")
    chunk: Chunk = Relationship(back_populates="chunk_queries")


if __name__ == "__main__":
    for table in SQLModel.metadata.sorted_tables:
        print(f"\n--- DDL for table: {table.name} ---")
        # Ajuste o dialeto conforme necessário (postgresql, mysql, etc.)
        print(CreateTable(table).compile(dialect=postgresql.dialect(), compile_kwargs={"indent": "    "}))
