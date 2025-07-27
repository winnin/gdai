from pathlib import Path

import pytest

from gdai.commons.enums import DocumentTypeEnum
from gdai.extractors.pdf_extractor import PDFExtractor


class TestPDFExtractor:
    """Test suite for the PDFExtractor."""

    @staticmethod
    def get_fixtures_path() -> Path:
        """Get the path to the fixtures directory."""
        # Assuming a standard structure with fixtures in tests/fixtures
        current_dir = Path(__file__).parent
        fixtures_path = current_dir.parent / "fixtures"

        return fixtures_path

    @pytest.fixture
    def pdf_extractor(self):
        """Return a PDFExtractor instance for testing."""
        return PDFExtractor()

    @pytest.fixture
    def sample_pdf_path_pdf_with_text_and_image(self):
        """Return the path to a sample PDF file for testing."""
        fixtures_path = self.get_fixtures_path()
        pdf_path = fixtures_path / "document_large_with_text_and_image.pdf"

        # Skip test if fixture doesn't exist
        if not pdf_path.exists():
            pytest.skip(f"Sample PDF fixture not found: {pdf_path}")
        return str(pdf_path)

    def test_extract_document_data(self, pdf_extractor, sample_pdf_path_pdf_with_text_and_image):
        """Test that extract_document_data extracts data from a PDF correctly."""
        tenant_id = "test-tenant"
        raw_document = pdf_extractor.extract_document_data(tenant_id, sample_pdf_path_pdf_with_text_and_image)

        assert raw_document.tenant_id == tenant_id
        assert raw_document.type == DocumentTypeEnum.pdf
        assert raw_document.name == "document_large_with_text_and_image.pdf"
        assert raw_document.path == sample_pdf_path_pdf_with_text_and_image

    def test_extract_text_content(self, pdf_extractor, sample_pdf_path_pdf_with_text_and_image):
        """Test that text is properly extracted from a PDF."""
        tenant_id = "test-tenant"

        raw_document = pdf_extractor.extract_document_data(tenant_id, sample_pdf_path_pdf_with_text_and_image)

        # Verify text extraction
        assert raw_document.texts is not None
        assert len(raw_document.texts) > 0

        # Check structure of extracted text
        for page_num, text in raw_document.texts:
            assert isinstance(page_num, int)
            assert isinstance(text, str)
            assert text.strip() != ""  # Text shouldn't be empty

    def test_invalid_pdf_handling(self, pdf_extractor):
        """Test handling of invalid PDF files."""
        fixtures_path = self.get_fixtures_path()
        invalid_pdf = fixtures_path / "invalid.pdf"

        # Create an empty file if it doesn't exist
        if not invalid_pdf.exists():
            invalid_pdf.touch()

        tenant_id = "test-tenant"

        # Should raise an exception for invalid PDF
        with pytest.raises(Exception):
            pdf_extractor.extract_document_data(tenant_id, str(invalid_pdf))
