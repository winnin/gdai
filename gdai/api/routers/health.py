"""Health check endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from gdai.repositories.database import DatabaseManager

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Overall health status")
    database: str = Field(..., description="Database connectivity status")

    class Config:
        json_schema_extra = {"example": {"status": "healthy", "database": "connected"}}


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check the health status of the API and its dependencies",
    tags=["health"],
)
async def health_check() -> HealthResponse:
    """Check API health status including database connectivity.

    Returns:
        HealthResponse: Health status information.
    """
    # Check database connectivity
    db_healthy = await DatabaseManager.health_check()

    return HealthResponse(
        status="healthy" if db_healthy else "unhealthy", database="connected" if db_healthy else "disconnected"
    )
