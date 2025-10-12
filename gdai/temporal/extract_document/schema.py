from dataclasses import dataclass, field


@dataclass
class DocumentExtracInput:
    s3_key: str  # S3 key of the document (e.g., tenant_id/filename)
    chunk_strategy: str
    tenant_id: str


@dataclass
class ChunkDocumentInput:
    document_id: str
    tenant_id: str
    chunk_strategy: str
    extracted_document_path: str


@dataclass
class Document:
    tenant_id: str = ""
    name: str = ""
    type: str = ""
    chunk_strategy: str = ""
    chunks: list["Chunk"] | None = field(default_factory=list)


@dataclass
class Chunk:
    id: str
    tenant_id: str
    document_id: str
    type: str
    chunk: str = ""
    page_number: int = 0
    embedding: list[float] | None = field(default_factory=list)
