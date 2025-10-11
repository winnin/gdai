"""Tests for health check endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from gdai.api.main import create_app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint returns 200."""
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]  # Depends on DB availability
    assert "database" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns API information."""
    app = create_app()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert data["name"] == "GDAI API"
