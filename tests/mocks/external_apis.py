"""Mocks for external API calls (Cohere, OpenAI, etc)."""

from typing import Any
from unittest.mock import MagicMock

import pytest


class MockCohereEmbedding:
    """Mock Cohere embedding response."""

    def __init__(self, embeddings: list[list[float]]):
        """Initialize mock embedding response.

        Args:
            embeddings: List of embedding vectors
        """
        self.float_ = embeddings


class MockCohereClient:
    """Mock Cohere API client."""

    def __init__(self, api_key: str):
        """Initialize mock Cohere client.

        Args:
            api_key: API key (not validated in mock)
        """
        self.api_key = api_key
        self.call_count = 0

    async def embed(
        self,
        texts: list[str],
        model: str = "embed-v4.0",
        input_type: str = "search_query",
        embedding_types: list[str] | None = None,
        **kwargs,
    ) -> Any:
        """Mock embed method.

        Args:
            texts: List of texts to embed
            model: Model name
            input_type: Input type
            embedding_types: Embedding types
            **kwargs: Additional arguments

        Returns:
            Mock response with embeddings
        """
        self.call_count += 1

        # Generate mock embeddings (1536 dimensions)
        embeddings = [[0.1] * 1536 for _ in texts]

        # Create mock response object
        response = MagicMock()
        response.embeddings = MockCohereEmbedding(embeddings)

        return response


class MockOpenAIMessage:
    """Mock OpenAI message response."""

    def __init__(self, content: str):
        """Initialize mock message.

        Args:
            content: Message content
        """
        self.content = content


class MockOpenAIClient:
    """Mock OpenAI ChatGPT client."""

    def __init__(self, **kwargs):
        """Initialize mock OpenAI client.

        Args:
            **kwargs: Client configuration (model_name, api_key, etc)
        """
        self.model_name = kwargs.get("model_name", "gpt-4o")
        self.api_key = kwargs.get("openai_api_key")
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 2000)
        self.streaming = kwargs.get("streaming", False)
        self.call_count = 0

    async def ainvoke(self, messages: list[Any]) -> MockOpenAIMessage:
        """Mock ainvoke method.

        Args:
            messages: List of messages

        Returns:
            Mock message response
        """
        self.call_count += 1

        # Generate mock response based on input
        if messages:
            prompt = str(messages[0].content) if hasattr(messages[0], "content") else str(messages[0])
            response_text = f"Mock LLM response to: {prompt[:50]}..."
        else:
            response_text = "Mock LLM response."

        return MockOpenAIMessage(response_text)


@pytest.fixture
def mock_cohere(monkeypatch):
    """Mock Cohere client globally.

    This fixture patches the Cohere AsyncClient to return a mock
    that simulates API calls without making real HTTP requests.

    Usage:
        def test_something(mock_cohere):
            # Cohere API calls are now mocked
            ...
    """
    monkeypatch.setattr("cohere.AsyncClient", MockCohereClient)
    yield MockCohereClient


@pytest.fixture
def mock_openai(monkeypatch):
    """Mock OpenAI client globally.

    This fixture patches the ChatOpenAI client to return a mock
    that simulates API calls without making real HTTP requests.

    Usage:
        def test_something(mock_openai):
            # OpenAI API calls are now mocked
            ...
    """
    monkeypatch.setattr("langchain_openai.ChatOpenAI", MockOpenAIClient)
    yield MockOpenAIClient


@pytest.fixture
def mock_cohere_with_error(monkeypatch):
    """Mock Cohere client that raises errors.

    Useful for testing error handling and retry logic.

    Usage:
        def test_error_handling(mock_cohere_with_error):
            # Cohere API calls will raise exceptions
            ...
    """

    class ErrorCohereClient(MockCohereClient):
        async def embed(self, *args, **kwargs):
            raise Exception("Mock API error: Rate limit exceeded")

    monkeypatch.setattr("cohere.AsyncClient", ErrorCohereClient)
    yield ErrorCohereClient


@pytest.fixture
def mock_openai_with_error(monkeypatch):
    """Mock OpenAI client that raises errors.

    Useful for testing error handling and retry logic.
    """

    class ErrorOpenAIClient(MockOpenAIClient):
        async def ainvoke(self, *args, **kwargs):
            raise Exception("Mock API error: Service unavailable")

    monkeypatch.setattr("langchain_openai.ChatOpenAI", ErrorOpenAIClient)
    yield ErrorOpenAIClient


# Helper functions for creating mock responses
def create_mock_embedding(dimension: int = 1536) -> list[float]:
    """Create a single mock embedding vector.

    Args:
        dimension: Embedding dimension (default: 1536 for Cohere)

    Returns:
        Mock embedding vector
    """
    return [0.1] * dimension


def create_mock_embeddings(count: int, dimension: int = 1536) -> list[list[float]]:
    """Create multiple mock embedding vectors.

    Args:
        count: Number of embeddings to create
        dimension: Embedding dimension

    Returns:
        List of mock embedding vectors
    """
    return [[0.1] * dimension for _ in range(count)]
