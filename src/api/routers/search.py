"""
Search endpoints router.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.deps import get_search_service
from src.api.models.search import SearchRequest, SearchResponse
from src.shared.logger import logger

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/query", response_model=SearchResponse)
async def search_query_endpoint(
    request: SearchRequest, search_service=Depends(get_search_service)
):
    """
    Process a search query and return results.
    """
    try:
        if not request.tenant_id or not request.query_id or not request.query_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="tenant_id, query_id, and query_text are required",
            )
        logger.info(
            f"Received search query for tenant: {request.tenant_id}, query_id: {request.query_id}"
        )
        query_result = await search_service.answer_query(
            request.tenant_id,
            request.query_id,
            request.query_text,
            request.chunks_limit,
        )
        return SearchResponse(
            message=query_result["msg"],
            list_chunks=query_result["chunks"],
            query_id=request.query_id,
            status="success",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing search query: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing search query: {e!s}",
        )
