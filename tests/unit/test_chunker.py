import pytest

from gdai.chunker.sentence_chunker import DocumentTextChunkerBySentence


class TestDocumentTextChunkerBySentence:
    """Test suite for the DocumentTextChunkerBySentence class."""

    @pytest.fixture
    def mock_text(self):
        text = [
            "This is the first sentence. This is the second sentence.",
            "This is the third sentence. This is the fourth sentence.",
            "This is the fifth sentence. This is the sixth sentence.",
        ]
        return text

    def test_chunk_with_multiple_sentences_per_chunk(self, mock_text):
        """Test chunking multiple pages of text."""
        # Test the chunker
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=2)
        result = chunker.chunk(mock_text)

        # Verify results
        assert len(result) == 3  # 3 chunks in 3 pages

        # Check page numbers are correct (1-indexed)
        assert result[0][0] == 1  # page 1
        assert result[0][1] == "This is the first sentence. This is the second sentence."

        assert result[1][0] == 2  # page 2
        assert result[1][1] == "This is the third sentence. This is the fourth sentence."

        assert result[2][0] == 3  # page 3
        assert result[2][1] == "This is the fifth sentence. This is the sixth sentence."

    def test_chunk_with_only_one_sentence_per_chunk(self, mock_text):
        """Test chunking with 1 sentence per chunk."""
        chunker = DocumentTextChunkerBySentence(
            min_sentences_per_chunks=1, max_char_per_chunk=30, character_overlap_per_chunk=2
        )
        result = chunker.chunk(mock_text)

        # Verify results
        assert len(result) == 6

    def test_chunk_with_empty_text(self):
        """Test chunking with empty text."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=1)
        result = chunker.chunk([])

        # Verify results
        assert len(result) == 0
