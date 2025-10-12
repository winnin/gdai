"""Pytest configuration for integration tests."""

import importlib
import sys

import pytest_asyncio


@pytest_asyncio.fixture(autouse=True, scope="function")
async def reload_repository_module(request):
    """Reload the repository module before each test to get fresh connections.

    This is necessary because the DatabaseManager caches the engine at class level,
    which gets bound to the first event loop. By disposing the engine and reloading
    the module, we ensure each test gets a fresh engine bound to its own event loop.

    This fixture only disposes the engine when a test is using db_session or db_engine,
    to ensure tables are properly set up via those fixtures.
    """
    # Check if the test is using db_session or db_engine fixtures
    uses_db_fixtures = any(fixture_name in request.fixturenames for fixture_name in ["db_session", "db_engine"])

    # Only dispose if the test uses database fixtures
    # This ensures tests that create their own engine will have tables set up first
    if uses_db_fixtures:
        from gdai.repositories.database import DatabaseManager

        await DatabaseManager.dispose()

        # Reload modules to clear singleton state
        if "gdai.repositories.database" in sys.modules:
            importlib.reload(sys.modules["gdai.repositories.database"])
        if "gdai.repositories.pgvector_repository" in sys.modules:
            importlib.reload(sys.modules["gdai.repositories.pgvector_repository"])
        if "gdai.repositories" in sys.modules:
            importlib.reload(sys.modules["gdai.repositories"])

    yield

    # Dispose the engine after each test to clean up
    if uses_db_fixtures:
        from gdai.repositories.database import DatabaseManager

        await DatabaseManager.dispose()
