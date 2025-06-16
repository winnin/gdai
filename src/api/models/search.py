from __future__ import annotations

from pydantic import BaseModel


class SearchRequest(BaseModel):
    """
    Request model for search queries.
    """

    tenant_id: str
    query_id: str
    query_text: str
    chunks_limit: int | None = 100


class SearchResponse(BaseModel):
    """
    Response model for search queries.
    """

    message: str
    query_id: str
    status: str
    list_chunks: list | None = None
