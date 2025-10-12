import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum, DocumentTypeEnum, QueryStatusEnum
from gdai.commons.settings import get_settings
from gdai.repositories.sqlalchemy import Base


class BaseModelMixin:
    """Base model for all tables."""

    __abstract__ = True

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=False), default=func.now())
    updated_at = Column(
        DateTime(timezone=False),
        default=func.now(),
        onupdate=func.now(),
    )


class DocumentModel(Base, BaseModelMixin):
    """Document model."""

    __tablename__ = "document"

    name = Column(String, default="")
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.processed, nullable=False)
    type = Column(Enum(DocumentTypeEnum), nullable=False)
    s3_path = Column(String, nullable=False, index=True)
    chunk_strategy = Column(Text, nullable=True)

    # Relationships
    chunks = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan", collection_class=list)


class ChunkModel(Base, BaseModelMixin):
    """Chunk model."""

    __tablename__ = "chunk"

    type = Column(Enum(ChunkTypeEnum), nullable=False)
    chunk = Column(Text, default="")
    page_number = Column(Integer)
    embedding = Column(Vector(get_settings().embedding.dimension))

    # Relationships
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"))
    document = relationship("DocumentModel", back_populates="chunks")

    chunk_queries = relationship("QueryChunkLinkModel", back_populates="chunk")


class QueryModel(Base, BaseModelMixin):
    """Query model."""

    __tablename__ = "query"

    query = Column(Text, default="")
    result = Column(Text, default="")
    similarity = Column(Text, default="cosine")
    status = Column(Enum(QueryStatusEnum), default=QueryStatusEnum.pending, nullable=False)

    # Relationships
    query_chunks = relationship("QueryChunkLinkModel", back_populates="query")


class QueryChunkLinkModel(Base, BaseModelMixin):
    """Query to Chunk link model."""

    __tablename__ = "query_chunk_link"

    query_id = Column(UUID(as_uuid=True), ForeignKey("query.id"))
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunk.id"))
    similarity_score = Column(Float, default=0.0)

    # Relationships
    query = relationship("QueryModel", back_populates="query_chunks")
    chunk = relationship("ChunkModel", back_populates="chunk_queries")
