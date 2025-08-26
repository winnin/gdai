from chonkie import SentenceChunker
from cleantext import clean

from gdai.chunkers.base_chunker import BaseChunker


class DocumentTextChunkerBySentence(BaseChunker):
    """Base class for sentence chunkers."""

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
