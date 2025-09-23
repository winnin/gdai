from dataclasses import dataclass, field


@dataclass
class SearchInput:
    query_id: str
    query: str
    tenant_id: str
    similarity_threshold: float = 0.75
    max_num_chunks: int = 20
    document_ids: list[str] | None = None


@dataclass
class QueryInput:
    query_id: str
    tenant_id: str
    query: str


@dataclass
class SearchQueryParam:
    tenant_id: str
    limit: int = 100
    similarity_threshold: float = 0.0
    document_ids: list[str] | None = None
    query_embedding: list[float] = field(default_factory=list)


@dataclass
class Chunk:
    chunk_id: str
    type: str
    text: str
    document_id: str
    page_number: int
    query_similarity: float


@dataclass
class PromptInput:
    query: str
    chunks: list[Chunk] = field(default_factory=list)


@dataclass
class SearchResult:
    query_id: str
    query: str
    answer: str
    tenant_id: str
    chunks: list[Chunk] = field(default_factory=list)
