"""Query execution endpoints."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from temporalio.client import Client

from gdai.api.dependencies import get_current_tenant, get_repository, get_temporal_client
from gdai.commons.enums import QueryStatusEnum
from gdai.commons.exceptions import QueryNotFoundError
from gdai.commons.logger import logger
from gdai.domain.query import QueryCreateDTO, QueryDTO, QueryListResponse, QueryResultDTO
from gdai.repositories.models import QueryModel
from gdai.repositories.pgvector_repository import PGVectorRepository
from gdai.temporal.search_on_documents.schema import SearchInput
from gdai.temporal.search_on_documents.workflow import DocumentSearchWorkflow

router = APIRouter()


@router.post(
    "/queries",
    response_model=QueryDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new query",
    description="Submit a query for processing against the document corpus",
    tags=["queries"],
)
async def create_query(
    query_input: QueryCreateDTO = Body(..., description="Query parameters"),
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
    temporal_client: Annotated[Client, Depends(get_temporal_client)] = None,
) -> QueryDTO:
    """Create a new query for processing.

    The query will be processed asynchronously. Use the query_id to check
    the status and retrieve results.

    Args:
        query_input: Query creation parameters.
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Returns:
        QueryDTO: Created query information.

    Raises:
        HTTPException: If query creation fails.
    """
    try:
        # Create query record
        query = QueryModel(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            query=query_input.query,
            status=QueryStatusEnum.pending,
            similarity="cosine",
            result="",
        )

        # Save to database with "pending" status
        query.status = QueryStatusEnum.pending
        query = await repository.insert_query(query)

        # Trigger Temporal workflow for query processing
        try:
            workflow_id = f"search-{query.id}"
            document_ids = [str(doc_id) for doc_id in query_input.document_ids] if query_input.document_ids else None

            await temporal_client.start_workflow(
                DocumentSearchWorkflow.run,
                SearchInput(
                    query_id=str(query.id),
                    query=query_input.query,
                    tenant_id=tenant_id,
                    similarity_threshold=query_input.similarity_threshold,
                    max_num_chunks=query_input.limit,
                    document_ids=document_ids,
                ),
                id=workflow_id,
                task_queue="search-queue",
            )
            logger.info(f"Started document search workflow {workflow_id} for query {query.id}")
        except Exception as e:
            logger.error(f"Failed to start workflow for query {query.id}: {e}")
            # Don't fail the request - workflow can be retried

        return QueryDTO.model_validate(query)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create query: {str(e)}"
        )


@router.get(
    "/queries/{query_id}",
    response_model=QueryResultDTO,
    status_code=status.HTTP_200_OK,
    summary="Get query result",
    description="Retrieve the result of a query by its ID",
    tags=["queries"],
)
async def get_query_result(
    query_id: str = Path(..., description="Query unique identifier"),
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
) -> QueryResultDTO:
    """Get query result by ID.

    Args:
        query_id: Query unique identifier.
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Returns:
        QueryResultDTO: Query result information.

    Raises:
        HTTPException: If query is not found.
    """
    try:
        query = await repository.get_query(tenant_id, query_id)

        if not query:
            raise QueryNotFoundError(tenant_id, query_id)

        # Get related chunks (if query is completed)
        relevant_chunks = []
        if query.status == QueryStatusEnum.completed:
            # TODO: Retrieve query-chunk links and format them
            # For now, return empty list
            pass

        return QueryResultDTO(
            query_id=query.id,
            query_text=query.query,
            result=query.result or "",
            status=query.status,
            relevant_chunks=relevant_chunks,
            processing_time_ms=None,  # TODO: Calculate from timestamps
        )

    except QueryNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve query: {str(e)}"
        )


@router.get(
    "/queries",
    response_model=QueryListResponse,
    status_code=status.HTTP_200_OK,
    summary="List all queries",
    description="Retrieve all queries for the current tenant",
    tags=["queries"],
)
async def list_queries(
    tenant_id: Annotated[str, Depends(get_current_tenant)] = None,
    repository: Annotated[PGVectorRepository, Depends(get_repository)] = None,
) -> QueryListResponse:
    """List all queries for the current tenant.

    Note: This endpoint currently retrieves all queries. In production,
    consider adding pagination parameters.

    Args:
        tenant_id: Tenant identifier from header.
        repository: Database repository instance.

    Returns:
        QueryListResponse: List of queries with total count.
    """
    try:
        queries = await repository.get_all_queries(tenant_id)

        query_dtos = [QueryDTO.model_validate(query) for query in queries]

        return QueryListResponse(queries=query_dtos, total=len(query_dtos))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to retrieve queries: {str(e)}"
        )
