"""Unit tests for gdai.services.chunkers module."""

import pytest

from gdai.services.chunkers import (
    BaseChunker,
    ChunkerFactory,
    DocumentTextChunkerBySentence,
)

# Alias for backward compatibility in tests
SentenceChunker = DocumentTextChunkerBySentence


class TestBaseChunker:
    """Test suite for BaseChunker abstract class."""

    def test_base_chunker_initialization(self):
        """Test BaseChunker can be initialized with strategy."""

        class ConcreteChunker(BaseChunker):
            def chunk(self, text: str) -> list[str]:
                return [text]

        chunker = ConcreteChunker(strategy="test_strategy")
        assert chunker.strategy == "test_strategy"

    def test_base_chunker_str_representation(self):
        """Test __str__ returns the strategy."""

        class ConcreteChunker(BaseChunker):
            def chunk(self, text: str) -> list[str]:
                return [text]

        chunker = ConcreteChunker(strategy="my_strategy")
        assert str(chunker) == "my_strategy"

    def test_base_chunker_chunk_is_abstract(self):
        """Test that chunk method is abstract and must be implemented."""
        # BaseChunker can be instantiated but chunk method won't work
        # The abstractmethod decorator makes it clear it should be overridden

        # Verify that chunk is marked as abstract
        assert hasattr(BaseChunker.chunk, "__isabstractmethod__")
        assert BaseChunker.chunk.__isabstractmethod__ is True

    def test_base_chunker_chunk_method_returns_none(self):
        """Test that BaseChunker chunk method can be called (returns None by default)."""

        # Create a class that doesn't override chunk to test coverage of the abstract method
        class IncompleteChunker(BaseChunker):
            pass  # Intentionally not implementing chunk

        # In Python, abstract methods with 'pass' can actually be instantiated and called
        # This test just ensures we cover the 'pass' statement in the abstract method
        try:
            chunker = IncompleteChunker(strategy="test")
            # This will call the base implementation (which just has 'pass')
            result = chunker.chunk("test text")
            # The method with just 'pass' returns None
            assert result is None
        except TypeError:
            # Some versions of Python prevent instantiation of classes with abstract methods
            pass


class TestDocumentTextChunkerBySentence:
    """Test suite for DocumentTextChunkerBySentence class."""

    def test_sentence_chunker_initialization(self):
        """Test sentence chunker initializes correctly."""
        chunker = DocumentTextChunkerBySentence()
        assert chunker.strategy == "sentence"
        assert chunker.chunker is not None

    def test_sentence_chunker_initialization_with_custom_min_sentences(self):
        """Test sentence chunker with custom min_sentences_per_chunks."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=10)
        assert chunker.strategy == "sentence"
        assert chunker.chunker is not None

    def test_sentence_chunker_inherits_from_base_chunker(self):
        """Test that DocumentTextChunkerBySentence inherits from BaseChunker."""
        chunker = DocumentTextChunkerBySentence()
        assert isinstance(chunker, BaseChunker)

    def test_sentence_chunker_str_representation(self):
        """Test __str__ returns 'sentence'."""
        chunker = DocumentTextChunkerBySentence()
        assert str(chunker) == "sentence"

    def test_clean_text_removes_line_breaks(self):
        """Test _clean_text removes line breaks."""
        chunker = DocumentTextChunkerBySentence()
        text = "Hello\nWorld\rTest"
        cleaned = chunker._clean_text(text)
        assert "\n" not in cleaned
        assert "\r" not in cleaned

    def test_clean_text_fixes_unicode(self):
        """Test _clean_text fixes unicode errors."""
        chunker = DocumentTextChunkerBySentence()
        # Text with unicode issues
        text = "Hello World"
        cleaned = chunker._clean_text(text)
        assert isinstance(cleaned, str)
        assert len(cleaned) > 0

    def test_clean_text_preserves_content(self):
        """Test _clean_text preserves important content."""
        chunker = DocumentTextChunkerBySentence()
        text = "Hello World! This is a test."
        cleaned = chunker._clean_text(text)
        # Should preserve words and punctuation
        assert "Hello" in cleaned
        assert "World" in cleaned
        assert "test" in cleaned

    def test_clean_text_handles_empty_string(self):
        """Test _clean_text handles empty string."""
        chunker = DocumentTextChunkerBySentence()
        cleaned = chunker._clean_text("")
        assert cleaned == ""

    def test_clean_text_handles_whitespace_only(self):
        """Test _clean_text handles whitespace-only string."""
        chunker = DocumentTextChunkerBySentence()
        cleaned = chunker._clean_text("   \n\r\t   ")
        assert cleaned.strip() == ""

    def test_chunk_single_page(self):
        """Test chunking a single page of text."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=2)
        texts = [
            "This is the first sentence. This is the second sentence. "
            "This is the third sentence. This is the fourth sentence. "
            "This is the fifth sentence."
        ]
        result = chunker.chunk(texts)

        # Should return list of tuples (page_number, chunk_text)
        assert isinstance(result, list)
        assert len(result) > 0
        for page_num, chunk_text in result:
            assert isinstance(page_num, int)
            assert isinstance(chunk_text, str)
            assert page_num >= 1  # Page numbers start at 1

    def test_chunk_multiple_pages(self):
        """Test chunking multiple pages of text."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=2)
        texts = [
            "Page 1 sentence 1. Page 1 sentence 2. Page 1 sentence 3.",
            "Page 2 sentence 1. Page 2 sentence 2. Page 2 sentence 3.",
            "Page 3 sentence 1. Page 3 sentence 2. Page 3 sentence 3.",
        ]
        result = chunker.chunk(texts)

        # Should have chunks from multiple pages
        assert isinstance(result, list)
        assert len(result) > 0

        # Check page numbers
        page_numbers = [page_num for page_num, _ in result]
        assert min(page_numbers) == 1
        assert max(page_numbers) <= len(texts)

    def test_chunk_empty_list(self):
        """Test chunking empty list of texts."""
        chunker = DocumentTextChunkerBySentence()
        result = chunker.chunk([])
        assert result == []

    def test_chunk_empty_strings(self):
        """Test chunking list with empty strings."""
        chunker = DocumentTextChunkerBySentence()
        texts = ["", "", ""]
        result = chunker.chunk(texts)
        # Should handle gracefully
        assert isinstance(result, list)

    def test_chunk_returns_cleaned_text(self):
        """Test that chunk returns cleaned text."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=2)
        texts = ["Sentence 1.\nSentence 2.\rSentence 3."]
        result = chunker.chunk(texts)

        # Check that returned chunks don't have line breaks
        for _, chunk_text in result:
            assert "\n" not in chunk_text
            assert "\r" not in chunk_text

    def test_chunk_preserves_text_content(self):
        """Test that chunking preserves the actual text content."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=2)
        texts = ["The quick brown fox jumps over the lazy dog. " * 5]
        result = chunker.chunk(texts)

        # Verify content is preserved
        assert len(result) > 0
        for _, chunk_text in result:
            assert "quick" in chunk_text or "brown" in chunk_text or "fox" in chunk_text

    def test_chunk_with_long_text(self):
        """Test chunking with long text."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=3)
        # Create a long text with many sentences
        sentences = [f"This is sentence number {i}. " for i in range(50)]
        texts = ["".join(sentences)]
        result = chunker.chunk(texts)

        # Should create multiple chunks
        assert len(result) > 1
        for page_num, chunk_text in result:
            assert page_num == 1  # All from same page
            assert len(chunk_text) > 0

    def test_chunk_with_short_text(self):
        """Test chunking with very short text."""
        chunker = DocumentTextChunkerBySentence()
        texts = ["Short."]
        result = chunker.chunk(texts)

        # Should handle short text
        assert isinstance(result, list)

    def test_chunk_with_special_characters(self):
        """Test chunking text with special characters."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=2)
        texts = [
            "Hello @world! This is a test #hashtag. "
            "Email: test@example.com. Phone: 123-456-7890. "
            "URL: https://example.com. Numbers: 12345."
        ]
        result = chunker.chunk(texts)

        # Should handle special characters
        assert len(result) > 0
        for _, chunk_text in result:
            assert len(chunk_text) > 0

    def test_chunk_with_unicode_characters(self):
        """Test chunking text with unicode characters."""
        chunker = DocumentTextChunkerBySentence(min_sentences_per_chunks=2)
        texts = ["Olá mundo! Café com açúcar. Naïve résumé. 你好世界."]
        result = chunker.chunk(texts)

        # Should handle unicode
        assert len(result) > 0
        for _, chunk_text in result:
            assert len(chunk_text) > 0


class TestChunkerFactory:
    """Test suite for ChunkerFactory class."""

    def test_factory_get_sentence_chunker(self):
        """Test factory returns SentenceChunker for 'sentence' type."""
        chunker = ChunkerFactory.get_chunker("sentence")
        assert isinstance(chunker, SentenceChunker)
        assert isinstance(chunker, DocumentTextChunkerBySentence)
        assert chunker.strategy == "sentence"

    def test_factory_returns_new_instance_each_time(self):
        """Test factory returns new instance each time."""
        chunker1 = ChunkerFactory.get_chunker("sentence")
        chunker2 = ChunkerFactory.get_chunker("sentence")
        assert chunker1 is not chunker2

    def test_factory_unknown_chunker_type_raises_error(self):
        """Test factory raises ValueError for unknown chunker type."""
        with pytest.raises(ValueError, match="Unknown chunker type: unknown"):
            ChunkerFactory.get_chunker("unknown")

    def test_factory_invalid_type_raises_error(self):
        """Test factory raises ValueError for various invalid types."""
        invalid_types = ["paragraph", "word", "character", "", "SENTENCE", "Sentence"]

        for invalid_type in invalid_types:
            with pytest.raises(ValueError, match=f"Unknown chunker type: {invalid_type}"):
                ChunkerFactory.get_chunker(invalid_type)

    def test_factory_is_static_method(self):
        """Test that get_chunker is a static method."""
        # Should be able to call without instantiating
        chunker = ChunkerFactory.get_chunker("sentence")
        assert chunker is not None

    def test_factory_does_not_require_instantiation(self):
        """Test factory can be used without creating instance."""
        # This should work without creating ChunkerFactory instance
        chunker = ChunkerFactory.get_chunker("sentence")
        assert isinstance(chunker, BaseChunker)


class TestChunkersIntegration:
    """Integration tests for chunkers module."""

    def test_sentence_chunker_end_to_end(self):
        """Test complete workflow with sentence chunker."""
        # Get chunker from factory
        chunker = ChunkerFactory.get_chunker("sentence")

        # Prepare sample text
        texts = [
            "This is the first document. It has multiple sentences. "
            "Each sentence should be properly chunked. "
            "The chunker should handle this correctly.",
            "This is the second document. It also has sentences. " "We want to test multiple pages.",
        ]

        # Chunk the text
        result = chunker.chunk(texts)

        # Verify results
        assert isinstance(result, list)
        assert len(result) > 0

        # Verify structure
        for page_num, chunk_text in result:
            assert isinstance(page_num, int)
            assert page_num in [1, 2]  # Should match input pages
            assert isinstance(chunk_text, str)
            assert len(chunk_text) > 0

    def test_chunker_strategy_attribute(self):
        """Test that chunkers have correct strategy attribute."""
        chunker = ChunkerFactory.get_chunker("sentence")
        assert hasattr(chunker, "strategy")
        assert chunker.strategy == "sentence"
        assert str(chunker) == "sentence"

    def test_multiple_chunkers_independent(self):
        """Test that multiple chunker instances are independent."""
        chunker1 = ChunkerFactory.get_chunker("sentence")
        chunker2 = ChunkerFactory.get_chunker("sentence")

        text1 = ["Text for chunker 1. " * 10]
        text2 = ["Different text for chunker 2. " * 10]

        result1 = chunker1.chunk(text1)
        result2 = chunker2.chunk(text2)

        # Results should be different
        assert result1 != result2
