from dataclasses import dataclass, field

from gdai.commons.enums import ChunkTypeEnum


@dataclass
class DocumentExtracInput:
    document_path: str
    chunk_strategy: str
    tenant_id: str


@dataclass
class ChunkDocumentInput:
    chunk_strategy: str
    extracted_document_path: str


@dataclass
class StoreDocumentInput:
    tenant_id: str
    chunk_strategy: str
    document_original_path: str
    document_chunks_path: str


@dataclass
class Document:
    name: str = ""
    tenant_id: str = ""
    type: str = ""
    chunk_strategy: str = ""
    chunks: list["Chunk"] | None = field(default_factory=list)


@dataclass
class Chunk:
    type: ChunkTypeEnum = ChunkTypeEnum.text
    chunk: str = ""
    page_number: int = 0
