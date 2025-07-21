from __future__ import annotations

import enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.config.sqlalchemy import Base


class DocumentStatusEnum(str, enum.Enum):
    uploaded = "uploaded"
    processing = "processing"
    processed = "processed"
    failed = "failed"


class DocumentTypeEnum(str, enum.Enum):
    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    # Adicione outros tipos conforme necessário


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


class QueryTypeEnum(str, enum.Enum):
    text = "text"
    image = "image"
    table = "table"


class DocumentModel(Base):
    __tablename__ = "document"
    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(String(64), nullable=False)
    name = Column(String, nullable=False)
    status = Column(Enum(DocumentStatusEnum, create_constraint=False, native_enum=False), default=DocumentStatusEnum.uploaded)
    type = Column(Enum(DocumentTypeEnum, create_constraint=False, native_enum=False), nullable=False)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # Relationship
    chunks = relationship("DocumentChunkModel", back_populates="document")


class DocumentChunkModel(Base):
    __tablename__ = "document_chunk"
    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(String(64), nullable=False)
    type = Column(Enum(ChunkTypeEnum, create_constraint=False, native_enum=False), nullable=False)
    chunk = Column(String, nullable=False)
    page_number = Column(Integer, nullable=False)
    embedding = Column(Vector(1536))
    fk_document_id = Column(UUID(as_uuid=True), ForeignKey("document.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # Relationship
    document = relationship("DocumentModel", back_populates="chunks")
    query_document_chunks = relationship("QueryDocumentChunkModel", back_populates="document_chunk")


class QueryModel(Base):
    __tablename__ = "query"
    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(String(64), nullable=False)
    query = Column(String, nullable=False)
    result = Column(String)
    status = Column(Enum(QueryStatusEnum, create_constraint=False, native_enum=False), nullable=False, default=QueryStatusEnum.pending)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # Relationship
    query_document_chunks = relationship("QueryDocumentChunkModel", back_populates="query")


class QueryDocumentChunkModel(Base):
    __tablename__ = "query_document_chunk"
    id = Column(UUID(as_uuid=True), primary_key=True)
    fk_document_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunk.id", ondelete="CASCADE"), nullable=False)
    fk_query_id = Column(UUID(as_uuid=True), ForeignKey("query.id", ondelete="CASCADE"), nullable=False)
    similarity_type = Column(Enum(SimilarityTypeEnum, create_constraint=False, native_enum=False), nullable=False, default=SimilarityTypeEnum.cosine)
    similarity_score = Column(Float, nullable=False)
    type = Column(Enum(QueryTypeEnum, create_constraint=False, native_enum=False), nullable=False)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # Relationships
    document_chunk = relationship("DocumentChunkModel", back_populates="query_document_chunks")
    query = relationship("QueryModel", back_populates="query_document_chunks")
