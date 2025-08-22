from commons.enums import ChunkTypeEnum, QueryStatusEnum

from .base import BaseModel


class ResultChunk(BaseModel):
    chunk: str
    type: ChunkTypeEnum
    document_id: str
    page_number: int
    similarity_score: float = 0.0


class QueryResult(BaseModel):
    query: str
    result: str
    status: QueryStatusEnum
    result_chunks: list[ResultChunk] | None = []
