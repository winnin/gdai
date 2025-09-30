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
    tenant_id: str = ""
    name: str = ""
    type: str = ""
    chunk_strategy: str = ""
    chunks: list["Chunk"] | None = field(default_factory=list)


@dataclass
class Chunk:
    id: str
    type: ChunkTypeEnum = ChunkTypeEnum.text
    chunk: str = ""
    page_number: int = 0
    embedding: list[float] | None = field(default_factory=list)


@dataclass
class TempFiles:
    extracted_document_file_path: str
    chunk_files: list[str] = field(default_factory=list)
    embedded_files: list[str] = field(default_factory=list)
