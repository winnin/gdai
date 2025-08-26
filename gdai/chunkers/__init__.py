from .sentence_chunker import DocumentTextChunkerBySentence as SentenceChunker  # noqa: F401


class ChunkerFactory:
    """Factory class to create chunkers based on the type."""

    @staticmethod
    def get_chunker(chunker_type: str):
        """Get a chunker instance based on the type."""
        if chunker_type == "sentence":
            return SentenceChunker()
        # Add more chunker types as needed
        else:
            raise ValueError(f"Unknown chunker type: {chunker_type}")
