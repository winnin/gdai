from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    message: str
    document_name: str
    tenant_id: str
    status: str = Field(default="pending")


class SearchRequest(BaseModel):
    tenant_id: str
    query_text: str
    chunks_limit: int = Field(default=10, ge=1, le=100)
    document_ids: list[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    tenant_id: str
    query_id: str
    query: str
    status: str = Field(default="success")
    result: str = Field(default="")
    list_chunks: list[dict] = Field(default_factory=list)


class DocumentStatusResponse(BaseModel):
    id: str
    name: str
    status: str
    tenant_id: str
    number_of_chunks: int = Field(default=0)
    number_of_embedded_chunks: int = Field(default=0)
    chunk_strategy: str = Field()
    created_at: str
    updated_at: str
