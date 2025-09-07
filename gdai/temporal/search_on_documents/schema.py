from dataclasses import dataclass, field


@dataclass
class SearchInput:
    query: str
    tenant_id: str
    max_num_chunks: int = 20
    document_ids: list[str] = field(default_factory=list)


@dataclass
class Chunk:
    chunk_id: str
    text: str
    page_number: int
    query_similarity: float


@dataclass
class SearchResult:
    query_id: str
    query: str
    answer: str
    tenant_id: str
    chunks: list[Chunk] = field(default_factory=list)
