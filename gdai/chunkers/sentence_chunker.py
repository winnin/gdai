from chonkie import SentenceChunker

from gdai.chunkers.base_chunker import BaseChunker


class DocumentTextChunkerBySentence(BaseChunker):
    """Base class for sentence chunkers."""

    def __init__(
        self, min_sentences_per_chunks: int = 5, max_char_per_chunk: int = 400, character_overlap_per_chunk: int = 100
    ):
        """Initialize the sentence chunker with any necessary parameters."""
        self.chunker = SentenceChunker(
            tokenizer_or_token_counter="character",
            chunk_size=max_char_per_chunk,  # Maximum tokens per chunk
            chunk_overlap=character_overlap_per_chunk,  # Overlap between chunks
            min_sentences_per_chunk=min_sentences_per_chunks,  # Minimum sentences in each chunk
        )

    def chunk(self, texts=list[str]) -> list[tuple[int, str]]:
        """Chunk the input text into smaller parts."""
        chunk_res = self.chunker.chunk_batch(texts)
        pages_chunks = []
        for page_number, chunks_page in enumerate(chunk_res):
            for chunk in chunks_page:
                pages_chunks.append((page_number + 1, chunk.text.strip()))
        return pages_chunks
