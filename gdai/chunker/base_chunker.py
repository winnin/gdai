class BaseChunker:
    """Base class for chunkers."""

    def __init__(self, **args):
        """Initialize the chunker with any necessary parameters."""

    def chunk(self, text: str) -> list[str]:
        """Chunk the input text into smaller parts."""
        return [text[i : i + self.chunk_size] for i in range(0, len(text), self.chunk_size)]
