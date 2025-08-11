"""Search endpoints router."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from gdai.api.deps import get_search_service
from gdai.config.logger import logger

from .types import SearchRequest

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/")
async def search_query_endpoint(request: SearchRequest, search_service=Depends(get_search_service)):
    """Process a search query and return results."""
    try:
        if not request.tenant_id or not request.query_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="tenant_id, query_id, and query_text are required"
            )
        logger.info(f"Received search query for tenant: {request.tenant_id}")
        query_result = await search_service.answer_query(
            tenant_id=request.tenant_id,
            query=request.query_text,
            chunks_limit=request.chunks_limit,
            document_ids_to_search=request.document_ids or [],
        )

        return query_result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing search query: {e!s}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing search query: {e!s}",
        )
