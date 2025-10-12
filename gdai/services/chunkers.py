"""Chunker services for document text processing.

This module provides text chunking functionality with different strategies.
"""

from abc import abstractmethod

from chonkie import SentenceChunker
from cleantext import clean


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


class DocumentTextChunkerBySentence(BaseChunker):
    """Sentence-based text chunker using Chonkie library."""

    def __init__(self, min_sentences_per_chunks: int = 5):
        """Initialize the sentence chunker with any necessary parameters."""
        self.chunker = SentenceChunker(
            tokenizer_or_token_counter="character",
            min_sentences_per_chunk=min_sentences_per_chunks,  # Minimum sentences in each chunk
            chunk_size=1000,
        )
        super().__init__(strategy="sentence")

    def _clean_text(self, text: str) -> str:
        """Clean the text by removing leading and trailing whitespace."""
        text = clean(
            text,
            fix_unicode=True,  # fix various unicode errors
            to_ascii=False,
            lower=False,
            no_line_breaks=True,  # remove \n and \r
            no_urls=False,  # remove URLs
            no_emails=False,
            no_phone_numbers=False,
            no_numbers=False,  # keep numbers (set to True if you want to remove)
            no_punct=False,  # keep punctuation
            replace_with_punct="",
        )
        return text

    def chunk(self, texts=list[str]) -> list[tuple[int, str]]:
        """Chunk the input text into smaller parts."""
        chunk_res = self.chunker.chunk_batch(texts)

        pages_chunks = []
        for page_number, chunks_page in enumerate(chunk_res):
            for chunk in chunks_page:
                pages_chunks.append((page_number + 1, self._clean_text(chunk.text)))
        return pages_chunks


class ChunkerFactory:
    """Factory class to create chunkers based on the type."""

    @staticmethod
    def get_chunker(chunker_type: str):
        """Get a chunker instance based on the type."""
        if chunker_type == "sentence":
            return DocumentTextChunkerBySentence()
        # Add more chunker types as needed
        else:
            raise ValueError(f"Unknown chunker type: {chunker_type}")
