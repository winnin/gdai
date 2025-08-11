import datetime

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    id: str
    message: str
    document_name: str
    tenant_id: str
    status: str = Field(default="pending")
    chunk_strategy: str


class SearchRequest(BaseModel):
    tenant_id: str
    query_text: str
    chunks_limit: int = Field(default=10, ge=1, le=100)
    document_ids: list[str] = Field(default_factory=list)


class SearchChunkResponse(BaseModel):
    id: str
    tenant_id: str
    chunk: str
    page: str
    similarity: float
    created_at: datetime.datetime
    updated_at: datetime.datetime


class SearchResponse(BaseModel):
    tenant_id: str
    query_id: str
    query: str
    status: str = Field(default="success")
    result: str = Field(default="")
    list_chunks: list[SearchChunkResponse] = Field(default_factory=list)


class DocumentStatusResponse(BaseModel):
    id: str
    name: str
    status: str
    tenant_id: str
    chunk_strategy: str = Field()
    number_of_chunks: int = Field(default=0)
    created_at: datetime.datetime
    updated_at: datetime.datetime
