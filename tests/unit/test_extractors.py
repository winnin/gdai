import os

import pytest

from gdai.extractors import ExtractorFactory


class TestPDFExtractor:
    """Test suite for the PDFExtractor class."""

    @pytest.fixture
    def sample_pdf_path(self):
        """Path to a sample PDF file for testing."""
        return "tests/fixtures/alice_in_wonderland_public_domain.pdf"

    @pytest.fixture
    def invalid_pdf_path(self):
        """Path to an invalid PDF file for testing."""
        return "tests/fixtures/invalid_file.pdf"

    @pytest.fixture
    def non_existent_path(self):
        """Path to a non-existent file for testing."""
        return "tests/fixtures/non_existent.pdf"

    def test_init_with_defaults(self):
        """Test extractor initialization with default parameters."""
        extractor = ExtractorFactory.get_extractor("pdf")
        assert extractor is not None
        assert hasattr(extractor, "extract_document_data")

    def test_factory_creates_pdf_extractor(self):
        """Test that factory creates correct extractor type."""
        extractor = ExtractorFactory.get_extractor("pdf")
        from gdai.extractors.pdf_extractor import PDFExtractor

        assert isinstance(extractor, PDFExtractor)

    def test_factory_unsupported_extractor_type(self):
        """Test factory with unsupported extractor type."""
        with pytest.raises(ValueError, match="Unknown extractor type"):
            ExtractorFactory.get_extractor("unsupported_type")

    def test_factory_ppt_extractor_not_implemented(self):
        """Test factory with PPT extractor (not implemented)."""
        with pytest.raises(NotImplementedError, match="PPT extractor is not implemented yet"):
            ExtractorFactory.get_extractor("ppt")

    @pytest.mark.skipif(
        not os.path.exists("tests/fixtures/alice_in_wonderland_public_domain.pdf"), reason="PDF fixture file not found"
    )
    def test_extract_document_data_valid_pdf(self, sample_pdf_path):
        """Test extracting data from a valid PDF file."""
        extractor = ExtractorFactory.get_extractor("pdf")
        result = extractor.extract_document_data(sample_pdf_path)

        # Verify structure
        assert isinstance(result, dict)
        assert "texts" in result
        assert "tables" in result
        assert "images" in result

        # Verify texts
        assert isinstance(result["texts"], list)
        if result["texts"]:
            for text_item in result["texts"]:
                assert isinstance(text_item, tuple)
                assert len(text_item) == 2
                page_num, text_content = text_item
                assert isinstance(page_num, int)
                assert isinstance(text_content, str)
                assert page_num >= 1

        # Verify tables and images (may be empty)
        assert isinstance(result["tables"], list)
        assert isinstance(result["images"], list)

    def test_extract_document_data_non_existent_file(self, non_existent_path):
        """Test extracting data from non-existent file."""
        extractor = ExtractorFactory.get_extractor("pdf")
        with pytest.raises(Exception):  # Should raise an exception
            extractor.extract_document_data(non_existent_path)

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_document_data_with_mocked_pdf(self, mock_pymupdf):
    #     """Test extraction with mocked PDF document."""
    #     # Setup mock
    #     mock_doc = Mock()
    #     mock_page = Mock()
    #     mock_page.get_text.return_value = "Sample text content from page 1"
    #     mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")
    #     result = extractor.extract_document_data("fake_path.pdf")

    #     # Verify calls
    #     mock_pymupdf.open.assert_called_once_with("fake_path.pdf")
    #     mock_doc.close.assert_called_once()
    #     mock_page.get_text.assert_called_once()

    #     # Verify result
    #     assert isinstance(result, dict)
    #     assert "texts" in result
    #     assert len(result["texts"]) == 1
    #     assert result["texts"][0] == (1, "Sample text content from page 1")

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_document_data_empty_pdf(self, mock_pymupdf):
    #     """Test extraction from PDF with no content."""
    #     # Setup mock for empty PDF
    #     mock_doc = Mock()
    #     mock_doc.__iter__ = Mock(return_value=iter([]))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")
    #     result = extractor.extract_document_data("empty.pdf")

    #     # Verify result
    #     assert isinstance(result, dict)
    #     assert result["texts"] == []
    #     assert result["tables"] == []
    #     assert result["images"] == []

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_document_data_multiple_pages(self, mock_pymupdf):
    #     """Test extraction from multi-page PDF."""
    #     # Setup mock for multiple pages
    #     mock_doc = Mock()
    #     mock_page1 = Mock()
    #     mock_page1.get_text.return_value = "Content from page 1"
    #     mock_page2 = Mock()
    #     mock_page2.get_text.return_value = "Content from page 2"
    #     mock_page3 = Mock()
    #     mock_page3.get_text.return_value = ""  # Empty page

    #     mock_doc.__iter__ = Mock(return_value=iter([mock_page1, mock_page2, mock_page3]))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")
    #     result = extractor.extract_document_data("multi_page.pdf")

    #     # Verify result - should only include pages with content
    #     assert len(result["texts"]) == 2
    #     assert result["texts"][0] == (1, "Content from page 1")
    #     assert result["texts"][1] == (2, "Content from page 2")

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_document_data_with_whitespace(self, mock_pymupdf):
    #     """Test extraction with whitespace handling."""
    #     # Setup mock
    #     mock_doc = Mock()
    #     mock_page = Mock()
    #     mock_page.get_text.return_value = "  \n\r  Text with whitespace  \n\r  "
    #     mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")
    #     result = extractor.extract_document_data("whitespace.pdf")

    #     # Verify whitespace is stripped
    #     assert len(result["texts"]) == 1
    #     assert result["texts"][0] == (1, "Text with whitespace")

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_document_data_pymupdf_exception(self, mock_pymupdf):
    #     """Test handling of PyMuPDF exceptions."""
    #     mock_pymupdf.open.side_effect = Exception("PDF parsing error")

    #     extractor = ExtractorFactory.get_extractor("pdf")
    #     with pytest.raises(Exception, match="PDF parsing error"):
    #         extractor.extract_document_data("corrupted.pdf")

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_raw_text_method(self, mock_pymupdf):
    #     """Test _extract_raw_text method functionality."""
    #     # Setup mock
    #     mock_doc = Mock()
    #     mock_page1 = Mock()
    #     mock_page1.get_text.return_value = "Page 1 content"
    #     mock_page2 = Mock()
    #     mock_page2.get_text.return_value = "Page 2 content"
    #     mock_doc.__iter__ = Mock(return_value=iter([mock_page1, mock_page2]))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")

    #     # Access the private method for testing
    #     texts = extractor._extract_raw_text(mock_doc)

    #     assert len(texts) == 2
    #     assert texts[0] == (1, "Page 1 content")
    #     assert texts[1] == (2, "Page 2 content")

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_raw_tables_method(self, mock_pymupdf):
    #     """Test _extract_raw_tables method (currently returns empty list)."""
    #     mock_doc = Mock()
    #     extractor = ExtractorFactory.get_extractor("pdf")

    #     # Access the private method for testing
    #     tables = extractor._extract_raw_tables(mock_doc)

    #     # Should return empty list as not implemented
    #     assert isinstance(tables, list)
    #     assert len(tables) == 0

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_raw_images_method(self, mock_pymupdf):
    #     """Test _extract_raw_images method (currently returns empty list)."""
    #     mock_doc = Mock()
    #     extractor = ExtractorFactory.get_extractor("pdf")

    #     # Access the private method for testing
    #     images = extractor._extract_raw_images(mock_doc)

    #     # Should return empty list as not implemented
    #     assert isinstance(images, list)
    #     assert len(images) == 0

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_document_close_called_on_success(self, mock_pymupdf):
    #     """Test that PDF document is properly closed after successful extraction."""
    #     mock_doc = Mock()
    #     mock_doc.__iter__ = Mock(return_value=iter([]))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")
    #     extractor.extract_document_data("test.pdf")

    #     # Verify close was called
    #     mock_doc.close.assert_called_once()

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_document_close_called_on_exception(self, mock_pymupdf):
    #     """Test that PDF document handling when exception occurs."""
    #     mock_doc = Mock()
    #     mock_doc.__iter__ = Mock(side_effect=Exception("Processing error"))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")

    #     with pytest.raises(Exception):
    #         extractor.extract_document_data("test.pdf")

    #     # Document may not be closed if exception occurs before close
    #     # This reflects current implementation behavior
    #     assert mock_doc.close.call_count == 0  # Currently not called on exception

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_extract_document_data_return_structure(self):
    #     """Test that extract_document_data returns correct structure."""
    #     with patch("gdai.extractors.pdf_extractor.pymupdf") as mock_pymupdf:
    #         mock_doc = Mock()
    #         mock_doc.__iter__ = Mock(return_value=iter([]))
    #         mock_pymupdf.open.return_value = mock_doc

    #         extractor = ExtractorFactory.get_extractor("pdf")
    #         result = extractor.extract_document_data("test.pdf")

    #         # Verify exact structure
    #         expected_keys = {"texts", "tables", "images"}
    #         assert set(result.keys()) == expected_keys
    #         assert all(isinstance(result[key], list) for key in expected_keys)

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_page_numbering_starts_from_one(self, mock_pymupdf):
    #     """Test that page numbering starts from 1, not 0."""
    #     mock_doc = Mock()
    #     mock_page = Mock()
    #     mock_page.get_text.return_value = "Test content"
    #     mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")
    #     result = extractor.extract_document_data("test.pdf")

    #     # First page should be numbered 1
    #     assert result["texts"][0][0] == 1

    # @patch("gdai.extractors.pdf_extractor.pymupdf")
    # def test_only_non_empty_text_included(self, mock_pymupdf):
    #     """Test that only pages with actual text content are included."""
    #     mock_doc = Mock()
    #     mock_page1 = Mock()
    #     mock_page1.get_text.return_value = "Valid content"
    #     mock_page2 = Mock()
    #     mock_page2.get_text.return_value = ""  # Empty
    #     mock_page3 = Mock()
    #     mock_page3.get_text.return_value = "   "  # Whitespace only
    #     mock_page4 = Mock()
    #     mock_page4.get_text.return_value = "Another valid content"

    #     mock_doc.__iter__ = Mock(return_value=iter([mock_page1, mock_page2, mock_page3, mock_page4]))
    #     mock_pymupdf.open.return_value = mock_doc

    #     extractor = ExtractorFactory.get_extractor("pdf")
    #     result = extractor.extract_document_data("test.pdf")

    #     # Should only include pages 1 and 4 (with actual content)
    #     assert len(result["texts"]) == 2
    #     assert result["texts"][0] == (1, "Valid content")
    #     assert result["texts"][1] == (4, "Another valid content")
