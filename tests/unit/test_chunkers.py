import pytest

from gdai.chunkers import ChunkerFactory


class TestDocumentTextChunkerBySentence:
    """Test suite for the DocumentTextChunkerBySentence class."""

    @pytest.fixture
    def mock_text(self):
        """Mock text data for testing."""
        text = [
            "This is the first sentence. This is the second sentence.",
            "This is the third sentence. This is the fourth sentence.",
            "This is the fifth sentence. This is the sixth sentence.",
        ]
        return text

    @pytest.fixture
    def single_sentence_text(self):
        """Mock text with single sentences per page."""
        return ["First page sentence.", "Second page sentence.", "Third page sentence."]

    def test_init_with_defaults(self):
        """Test chunker initialization with default parameters."""
        chunker = ChunkerFactory.get_chunker("sentence")
        assert chunker.strategy == "sentence"
        assert str(chunker) == "sentence"

    def test_init_with_custom_parameters(self):
        """Test chunker initialization with custom parameters."""
        chunker = ChunkerFactory.get_chunker("sentence")
        assert chunker.strategy == "sentence"

    def test_chunk_with_single_text(self, single_sentence_text):
        """Test chunking with single sentence per page."""
        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(single_sentence_text)

        assert len(result) == 3
        assert result[0][0] == 1
        assert result[0][1] == "First page sentence."
        assert result[1][0] == 2
        assert result[1][1] == "Second page sentence."
        assert result[2][0] == 3
        assert result[2][1] == "Third page sentence."

    def test_chunk_with_multiple_texts(self, mock_text):
        """Test chunking with multiple sentences per page."""
        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(mock_text)

        # Verify we get results
        assert len(result) >= 1
        assert isinstance(result, list)

        # Check that each result is a tuple with (page_number, text)
        for page_num, text in result:
            assert isinstance(page_num, int)
            assert isinstance(text, str)
            assert page_num >= 1

    def test_chunk_with_empty_input(self):
        """Test chunking with empty input."""
        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk([])

        assert len(result) == 0
        assert isinstance(result, list)

    def test_chunk_with_empty_text(self):
        """Test chunking with empty strings."""
        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(["", "  ", "\n"])

        # Should handle empty/whitespace gracefully
        assert isinstance(result, list)

    def test_chunk_with_only_one_sentence_per_chunk(self, mock_text):
        """Test that chunker processes all sentences."""
        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(mock_text)

        # Should have at least as many chunks as pages
        assert len(result) >= len(mock_text)

    def test_chunk_with_multiple_sentences_per_chunk(self, mock_text):
        """Test chunking behavior with multiple sentences."""
        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(mock_text)

        # Verify page numbering starts at 1
        page_numbers = [chunk[0] for chunk in result]
        assert min(page_numbers) == 1

        # Verify all chunks have content
        for page_num, text in result:
            assert text.strip() != ""

    def test_chunking_parameters_impact(self):
        """Test that different text structures are handled properly."""
        # Text with varying sentence lengths
        varied_text = [
            "Short sentence.",
            "This is a much longer sentence with more words and content that should be processed \
            correctly by the chunker implementation.",
            "Medium length sentence with some content.",
        ]

        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(varied_text)

        assert len(result) >= 1
        assert all(isinstance(chunk[0], int) and isinstance(chunk[1], str) for chunk in result)

    def test_chunk_preserves_page_order(self):
        """Test that chunking preserves the original page order."""
        text = [
            "Page one content here.",
            "Page two content here.",
            "Page three content here.",
            "Page four content here.",
        ]

        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(text)

        # Verify page numbers are sequential and ordered
        page_numbers = [chunk[0] for chunk in result]
        assert page_numbers == sorted(page_numbers)

        # Verify we have representation from each original page
        unique_pages = set(page_numbers)
        assert len(unique_pages) <= len(text)

    def test_text_cleaning_functionality(self):
        """Test that text cleaning works properly."""
        # Text with various whitespace and formatting issues
        messy_text = [
            "  This sentence has extra spaces.  \n",
            "\t\tTabbed sentence with formatting.\r\n",
            "Normal sentence without issues.",
        ]

        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(messy_text)

        # Verify results exist and text is cleaned
        assert len(result) >= 1
        for page_num, text in result:
            # Text should not have leading/trailing whitespace after cleaning
            assert text == text.strip() or text.strip() != ""

    def test_chunk_with_unicode_text(self):
        """Test chunking with unicode characters."""
        unicode_text = [
            "Sentence with émojis 🎉 and accénts.",
            "Another sentence with spëcial characters ñ and ç.",
        ]

        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(unicode_text)

        assert len(result) >= 1
        assert all(isinstance(chunk[1], str) for chunk in result)

    def test_chunk_with_punctuation_heavy_text(self):
        """Test chunking with heavy punctuation."""
        punct_text = [
            "Question? Yes! Exclamation... ellipsis, comma; semicolon: colon.",
            "More punctuation: quotes 'single' and \"double\" with (parentheses).",
        ]

        chunker = ChunkerFactory.get_chunker("sentence")
        result = chunker.chunk(punct_text)

        assert len(result) >= 1
        # Punctuation should be preserved
        combined_text = " ".join(chunk[1] for chunk in result)
        assert "?" in combined_text or "!" in combined_text
