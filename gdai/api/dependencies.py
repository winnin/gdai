"""Dependency injection for FastAPI endpoints."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Header, HTTPException, status
from temporalio.client import Client

from gdai.repositories.pgvector_repository import PGVectorRepository
from gdai.temporal.client import TemporalClientManager


async def get_repository() -> AsyncGenerator[PGVectorRepository, None]:
    """Get repository instance with session management.

    This dependency provides a PGVectorRepository with automatic session lifecycle.
    The session is created when the request starts and closed when it ends.

    Yields:
        PGVectorRepository: Repository instance with active database session.
    """
    async with PGVectorRepository() as repo:
        yield repo


async def get_current_tenant(x_tenant_id: str = Header(..., description="Tenant identifier")) -> str:
    """Extract tenant_id from request headers.

    Args:
        x_tenant_id: Tenant ID from X-Tenant-ID header.

    Returns:
        str: The tenant identifier.

    Raises:
        HTTPException: If tenant ID is missing or invalid.
    """
    if not x_tenant_id or not x_tenant_id.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing or invalid X-Tenant-ID header")
    return x_tenant_id.strip()


async def get_temporal_client() -> Client:
    """Get Temporal client instance.

    Returns:
        Client: Temporal client for workflow execution.

    Raises:
        HTTPException: If Temporal client is not available.
    """
    try:
        return await TemporalClientManager.get_client()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Temporal service unavailable: {str(e)}"
        )
