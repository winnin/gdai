import datetime
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from gdai.commons.enums import ChunkTypeEnum, DocumentStatusEnum, DocumentTypeEnum, QueryStatusEnum, SimilarityTypeEnum
from gdai.config.sqlalchemy import Base


class BaseModel:
    """Base model for all tables."""

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=False), default=datetime.datetime.now())
    updated_at = Column(
        DateTime(timezone=False),
        default=datetime.datetime.now(),
        onupdate=datetime.datetime.now(),
    )


class QueryChunkLinkModel(Base):
    """Query to Chunk link model."""

    __tablename__ = "query_chunk_link"

    query_id = Column(UUID(as_uuid=True), ForeignKey("query.id"), primary_key=True)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("chunk.id"), primary_key=True)
    similarity_score = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=False), default=datetime.datetime.now())
    updated_at = Column(
        DateTime(timezone=False),
        default=datetime.datetime.now(),
        onupdate=datetime.datetime.now(),
    )

    # Relationships
    query = relationship("QueryModel", back_populates="query_chunks")
    chunk = relationship("ChunkModel", back_populates="chunk_queries")


class QueryModel(Base, BaseModel):
    """Query model."""

    __tablename__ = "query"

    query = Column(Text, default="")
    result = Column(Text, default="")
    status = Column(Enum(QueryStatusEnum), default=QueryStatusEnum.pending)
    similarity = Column(Enum(SimilarityTypeEnum), default=SimilarityTypeEnum.cosine)

    # Relationships
    query_chunks = relationship("QueryChunkLinkModel", back_populates="query")


class ChunkModel(Base, BaseModel):
    """Chunk model."""

    __tablename__ = "chunk"

    type = Column(Enum(ChunkTypeEnum), nullable=False)
    chunk = Column(Text, default="")
    page_number = Column(Integer)
    embedding = Column(Vector)

    # Relationships
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"))
    document = relationship("DocumentModel", back_populates="chunks")

    chunk_queries = relationship("QueryChunkLinkModel", back_populates="chunk")


class DocumentModel(Base, BaseModel):
    """Document model."""

    __tablename__ = "document"

    name = Column(String, default="")
    status = Column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.uploaded)
    type = Column(Enum(DocumentTypeEnum), default=DocumentTypeEnum.pdf)

    # Relationships
    chunks = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan", collection_class=list)
