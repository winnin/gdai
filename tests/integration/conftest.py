"""Pytest configuration for integration tests."""

import importlib
import sys

import pytest


@pytest.fixture(autouse=True, scope="function")
def reload_repository_module():
    """Reload the repository module before each test to get fresh connections.

    This is necessary because the repository uses module-level engine/SessionLocal
    which gets bound to the first event loop. By reloading the module, we ensure
    each test gets a fresh engine bound to its own event loop.
    """
    # Reload the sqlalchemy module to get fresh engine and SessionLocal
    if "gdai.repositories.sqlalchemy" in sys.modules:
        importlib.reload(sys.modules["gdai.repositories.sqlalchemy"])

    # Reload the repository module to use the new sqlalchemy module
    if "gdai.repositories.pgvector_repository" in sys.modules:
        importlib.reload(sys.modules["gdai.repositories.pgvector_repository"])

    yield

    # No cleanup needed - next test will reload again
