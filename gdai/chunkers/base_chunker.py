from abc import abstractmethod


class BaseChunker:
    """Base class for chunkers."""

    def __init__(self, strategy: str):
        """Initialize the chunker with any necessary parameters."""
        self.strategy = strategy

    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        """Chunk the input text into smaller parts."""
        pass

    def __str__(self) -> str:
        """Return a string representation of the chunker."""
        return self.strategy
