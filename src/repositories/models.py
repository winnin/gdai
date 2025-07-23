import datetime
import enum
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


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


class BaseModel:
    """Base model for all tables."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))


class Document(Base, BaseModel):
    """Document model."""

    __tablename__ = "document"

    name = Column(String, default="")
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.uploaded)
    type = Column(Enum(DocumentTypeEnum), default=DocumentTypeEnum.pdf)

    # Relationships
    chunks = relationship("Chunk", back_populates="document", cascade="all, delete-orphan")


class Chunk(Base, BaseModel):
    """Chunk model."""

    __tablename__ = "chunk"

    type = Column(Enum(ChunkTypeEnum), nullable=False)
    chunk = Column(Text, default="")
    page_number = Column(Integer)
    embedding = Column(Vector)

    # Relationships
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"))
    document = relationship("Document", back_populates="chunks")

    chunk_queries = relationship("QueryChunkLink", back_populates="chunk")


class Query(Base, BaseModel):
    """Query model."""

    __tablename__ = "query"

    query = Column(Text, default="")
    result = Column(Text, default="")
    status = Column(Enum(QueryStatusEnum), default=QueryStatusEnum.pending)
    similarity = Column(Enum(SimilarityTypeEnum), default=SimilarityTypeEnum.cosine)

    # Relationships
    query_chunks = relationship("QueryChunkLink", back_populates="query")


class QueryChunkLink(Base):
    """Query to Chunk link model."""

    __tablename__ = "query_chunk_link"

    query_id = Column(UUID(as_uuid=True), ForeignKey("query.id"), primary_key=True)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunk.id"), primary_key=True)
    similarity_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))

    # Relationships
    query = relationship("Query", back_populates="query_chunks")
    chunk = relationship("Chunk", back_populates="chunk_queries")
