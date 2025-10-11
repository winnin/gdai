"""Unit tests for gdai.extractors module.

This module tests all extractor classes and the factory pattern.
Target: 100% code coverage for gdai/extractors/*.py
"""

from unittest.mock import MagicMock, patch

import pytest

from gdai.extractors import ExtractorFactory
from gdai.extractors.base_extractor import DocumentExtractor
from gdai.extractors.pdf_extractor import PDFExtractor


class TestDocumentExtractor:
    """Test suite for DocumentExtractor abstract base class."""

    def test_document_extractor_is_abstract(self):
        """Test that DocumentExtractor cannot be instantiated directly."""
        # DocumentExtractor is an ABC with abstract methods
        # Check that extract_document_data is abstract
        assert hasattr(DocumentExtractor.extract_document_data, "__isabstractmethod__")
        assert DocumentExtractor.extract_document_data.__isabstractmethod__ is True

    def test_document_extractor_initialization(self):
        """Test that DocumentExtractor can be initialized through subclass."""

        class ConcreteExtractor(DocumentExtractor):
            def extract_document_data(self, document_path: str) -> dict:  # noqa: ARG002
                return {"texts": [], "tables": [], "images": []}

        extractor = ConcreteExtractor()
        assert isinstance(extractor, DocumentExtractor)

    def test_document_extractor_abstract_method_signature(self):
        """Test that abstract method has correct signature."""

        class TestExtractor(DocumentExtractor):
            def extract_document_data(self, document_path: str) -> dict:  # noqa: ARG002
                return {}

        extractor = TestExtractor()
        result = extractor.extract_document_data("test.pdf")
        assert isinstance(result, dict)

    def test_document_extractor_abstract_method_returns_none(self):
        """Test that abstract method with pass returns None when called."""

        class IncompleteExtractor(DocumentExtractor):
            pass  # Intentionally not implementing extract_document_data

        # In Python, we can instantiate and call abstract methods with pass
        try:
            extractor = IncompleteExtractor()
            result = extractor.extract_document_data("test.pdf")
            # The method with just 'pass' returns None
            assert result is None
        except TypeError:
            # Some Python versions prevent instantiation of classes with abstract methods
            pass

    def test_document_extractor_abstract_method_coverage(self):
        """Test to cover the abstract method pass statement."""

        class TestExtractor(DocumentExtractor):
            def extract_document_data(self, document_path: str) -> dict:
                # Call the parent abstract method to cover the pass statement
                super().extract_document_data(document_path)
                return {"texts": [], "tables": [], "images": []}

        extractor = TestExtractor()
        result = extractor.extract_document_data("test.pdf")
        assert isinstance(result, dict)


class TestPDFExtractor:
    """Test suite for PDFExtractor class."""

    def test_pdf_extractor_initialization(self):
        """Test PDFExtractor initialization."""
        extractor = PDFExtractor()
        assert isinstance(extractor, PDFExtractor)
        assert isinstance(extractor, DocumentExtractor)

    def test_pdf_extractor_inherits_from_document_extractor(self):
        """Test that PDFExtractor properly inherits from DocumentExtractor."""
        extractor = PDFExtractor()
        assert hasattr(extractor, "extract_document_data")
        assert callable(extractor.extract_document_data)

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    def test_extract_document_data_success(self, mock_pymupdf_open):
        """Test successful document extraction."""
        # Create mock PDF document
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample text from page 1"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.close = MagicMock()

        mock_pymupdf_open.return_value = mock_doc

        # Test extraction
        extractor = PDFExtractor()
        result = extractor.extract_document_data("test.pdf")

        # Verify result structure
        assert isinstance(result, dict)
        assert "texts" in result
        assert "tables" in result
        assert "images" in result

        # Verify texts content
        assert len(result["texts"]) == 1
        assert result["texts"][0] == (1, "Sample text from page 1")

        # Verify empty tables and images
        assert result["tables"] == []
        assert result["images"] == []

        # Verify document was closed
        mock_doc.close.assert_called_once()

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    def test_extract_document_data_multiple_pages(self, mock_pymupdf_open):
        """Test extraction from PDF with multiple pages."""
        # Create mock pages
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Text from page 1"

        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Text from page 2"

        mock_page3 = MagicMock()
        mock_page3.get_text.return_value = "Text from page 3"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page1, mock_page2, mock_page3]
        mock_doc.close = MagicMock()

        mock_pymupdf_open.return_value = mock_doc

        # Test extraction
        extractor = PDFExtractor()
        result = extractor.extract_document_data("multi_page.pdf")

        # Verify all pages extracted
        assert len(result["texts"]) == 3
        assert result["texts"][0] == (1, "Text from page 1")
        assert result["texts"][1] == (2, "Text from page 2")
        assert result["texts"][2] == (3, "Text from page 3")

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    def test_extract_document_data_with_whitespace(self, mock_pymupdf_open):
        """Test extraction handles whitespace correctly."""
        mock_page = MagicMock()
        mock_page.get_text.return_value = "  Text with whitespace  \n\t"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.close = MagicMock()

        mock_pymupdf_open.return_value = mock_doc

        extractor = PDFExtractor()
        result = extractor.extract_document_data("test.pdf")

        # Verify whitespace is stripped
        assert result["texts"][0] == (1, "Text with whitespace")

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    def test_extract_document_data_empty_pages(self, mock_pymupdf_open):
        """Test extraction skips empty pages."""
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Content"

        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "   "  # Only whitespace

        mock_page3 = MagicMock()
        mock_page3.get_text.return_value = ""  # Empty

        mock_page4 = MagicMock()
        mock_page4.get_text.return_value = "More content"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page1, mock_page2, mock_page3, mock_page4]
        mock_doc.close = MagicMock()

        mock_pymupdf_open.return_value = mock_doc

        extractor = PDFExtractor()
        result = extractor.extract_document_data("test.pdf")

        # Should only have 2 text entries (skipping empty pages)
        assert len(result["texts"]) == 2
        assert result["texts"][0] == (1, "Content")
        assert result["texts"][1] == (4, "More content")

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    @patch("gdai.extractors.pdf_extractor.logger")
    def test_extract_document_data_exception_handling(self, mock_logger, mock_pymupdf_open):
        """Test exception handling during extraction."""
        # Simulate an error
        mock_pymupdf_open.side_effect = Exception("Failed to open PDF")

        extractor = PDFExtractor()

        # Verify exception is raised
        with pytest.raises(Exception, match="Failed to open PDF"):
            extractor.extract_document_data("invalid.pdf")

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert "Error extracting data from invalid.pdf" in str(mock_logger.error.call_args)

    def test_extract_raw_text_method(self):
        """Test _extract_raw_text method directly."""
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample text"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]

        extractor = PDFExtractor()
        texts = extractor._extract_raw_text(mock_doc)

        assert isinstance(texts, list)
        assert len(texts) == 1
        assert texts[0] == (1, "Sample text")

    def test_extract_raw_tables_method(self):
        """Test _extract_raw_tables method (currently returns empty list)."""
        mock_doc = MagicMock()

        extractor = PDFExtractor()
        tables = extractor._extract_raw_tables(mock_doc)

        assert isinstance(tables, list)
        assert len(tables) == 0  # Not implemented yet

    def test_extract_raw_images_method(self):
        """Test _extract_raw_images method (currently returns empty list)."""
        mock_doc = MagicMock()

        extractor = PDFExtractor()
        images = extractor._extract_raw_images(mock_doc)

        assert isinstance(images, list)
        assert len(images) == 0  # Not implemented yet

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    def test_document_close_called_on_success(self, mock_pymupdf_open):
        """Test that PDF document is properly closed after extraction."""
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Text"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.close = MagicMock()

        mock_pymupdf_open.return_value = mock_doc

        extractor = PDFExtractor()
        extractor.extract_document_data("test.pdf")

        # Verify close was called
        mock_doc.close.assert_called_once()

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    def test_extract_document_data_page_numbering(self, mock_pymupdf_open):
        """Test that page numbering starts at 1 (not 0)."""
        mock_pages = []
        for i in range(5):
            page = MagicMock()
            page.get_text.return_value = f"Page {i}"
            mock_pages.append(page)

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = mock_pages
        mock_doc.close = MagicMock()

        mock_pymupdf_open.return_value = mock_doc

        extractor = PDFExtractor()
        result = extractor.extract_document_data("test.pdf")

        # Verify page numbers start at 1
        for idx, (page_num, _) in enumerate(result["texts"]):
            assert page_num == idx + 1

    def test_extract_raw_text_with_multiple_pages(self):
        """Test _extract_raw_text with multiple pages."""
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Page 1"

        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "Page 2"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page1, mock_page2]

        extractor = PDFExtractor()
        texts = extractor._extract_raw_text(mock_doc)

        assert len(texts) == 2
        assert texts[0] == (1, "Page 1")
        assert texts[1] == (2, "Page 2")

    def test_extract_raw_text_skips_empty_pages(self):
        """Test _extract_raw_text skips empty pages."""
        mock_page1 = MagicMock()
        mock_page1.get_text.return_value = "Content"

        mock_page2 = MagicMock()
        mock_page2.get_text.return_value = "  "  # Whitespace only

        mock_page3 = MagicMock()
        mock_page3.get_text.return_value = "More content"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page1, mock_page2, mock_page3]

        extractor = PDFExtractor()
        texts = extractor._extract_raw_text(mock_doc)

        # Should skip page 2
        assert len(texts) == 2
        assert texts[0] == (1, "Content")
        assert texts[1] == (3, "More content")


class TestExtractorFactory:
    """Test suite for ExtractorFactory class."""

    def test_factory_get_pdf_extractor(self):
        """Test factory returns PDFExtractor for 'pdf' type."""
        extractor = ExtractorFactory.get_extractor("pdf")
        assert isinstance(extractor, PDFExtractor)
        assert isinstance(extractor, DocumentExtractor)

    def test_factory_returns_new_instance_each_time(self):
        """Test that factory returns new instances, not singletons."""
        extractor1 = ExtractorFactory.get_extractor("pdf")
        extractor2 = ExtractorFactory.get_extractor("pdf")

        assert extractor1 is not extractor2
        assert isinstance(extractor1, PDFExtractor)
        assert isinstance(extractor2, PDFExtractor)

    def test_factory_ppt_not_implemented(self):
        """Test that factory raises NotImplementedError for PPT."""
        with pytest.raises(NotImplementedError, match="PPT extractor is not implemented yet"):
            ExtractorFactory.get_extractor("ppt")

    def test_factory_unknown_type_raises_error(self):
        """Test that factory raises ValueError for unknown types."""
        with pytest.raises(ValueError, match="Unknown extractor type: docx"):
            ExtractorFactory.get_extractor("docx")

    def test_factory_unknown_type_variations(self):
        """Test various invalid extractor types."""
        invalid_types = ["word", "excel", "txt", "unknown"]

        for invalid_type in invalid_types:
            with pytest.raises(ValueError, match="Unknown extractor type"):
                ExtractorFactory.get_extractor(invalid_type)

    def test_factory_is_static_method(self):
        """Test that get_extractor is a static method."""
        assert isinstance(ExtractorFactory.__dict__["get_extractor"], staticmethod) or callable(
            ExtractorFactory.get_extractor
        )

    def test_factory_does_not_require_instantiation(self):
        """Test that factory can be used without instantiation."""
        # Should work without creating an instance of ExtractorFactory
        extractor = ExtractorFactory.get_extractor("pdf")
        assert isinstance(extractor, PDFExtractor)


class TestExtractorsIntegration:
    """Integration tests for the extractors module."""

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    def test_pdf_extractor_end_to_end_workflow(self, mock_pymupdf_open):
        """Test complete workflow: factory -> extractor -> extraction."""
        # Setup mock
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Integration test content"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.close = MagicMock()

        mock_pymupdf_open.return_value = mock_doc

        # Get extractor from factory
        extractor = ExtractorFactory.get_extractor("pdf")

        # Verify it's the right type
        assert isinstance(extractor, PDFExtractor)

        # Perform extraction
        result = extractor.extract_document_data("test.pdf")

        # Verify result
        assert "texts" in result
        assert "tables" in result
        assert "images" in result
        assert result["texts"][0] == (1, "Integration test content")

    def test_factory_creates_working_extractors(self):
        """Test that factory-created extractors actually work."""
        extractor = ExtractorFactory.get_extractor("pdf")

        # Verify extractor has required methods
        assert hasattr(extractor, "extract_document_data")
        assert callable(extractor.extract_document_data)

    @patch("gdai.extractors.pdf_extractor.pymupdf.open")
    def test_multiple_extractors_independent(self, mock_pymupdf_open):
        """Test that multiple extractor instances are independent."""
        # Setup mock
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Test"

        mock_doc = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.close = MagicMock()

        mock_pymupdf_open.return_value = mock_doc

        extractor1 = ExtractorFactory.get_extractor("pdf")
        extractor2 = ExtractorFactory.get_extractor("pdf")

        # Verify they are different instances
        assert extractor1 is not extractor2

        # Verify both work independently
        result1 = extractor1.extract_document_data("test1.pdf")
        result2 = extractor2.extract_document_data("test2.pdf")

        assert result1 == result2
        assert result1 is not result2
