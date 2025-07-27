import os
from unittest.mock import patch

import pytest

from gdai.extractors.exceptions import FileNotFoundException
from gdai.services.document_service import ExtractDocumentService


class TestExtractDocumentService:
    """Test suite for the ExtractDocumentService."""

    @pytest.fixture
    def document_service(self):
        """Return a ExtractDocumentService instance for testing."""
        return ExtractDocumentService()

    @staticmethod
    def get_test_file_path(filename):
        """Get path to a test file in fixtures directory."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        fixtures_path = os.path.join(current_dir, "..", "fixtures")
        return os.path.join(fixtures_path, filename)

    @pytest.fixture
    def valid_document_data(get_test_file_path):
        """Return valid document data for testing."""
        return {
            "tenant_id": "test-tenant",
            "document_path": TestExtractDocumentService.get_test_file_path("document_large_with_text_and_image.pdf"),
        }

    def test_read_file(self, document_service, valid_document_data):
        """Test that extract_data_from_document reads a file successfully."""
        tenant_id = valid_document_data["tenant_id"]
        document_path = valid_document_data["document_path"]
        document = document_service.extract_data_from_document(tenant_id, document_path)
        assert document.tenant_id == tenant_id
        assert document.name == "document.pdf"

    @pytest.mark.parametrize(
        "missing_file,empty_tenant",
        [
            (True, False),  # Missing file
            (False, True),  # Empty tenant ID
        ],
    )
    def test_validation_errors(self, document_service, missing_file, empty_tenant):
        """Test validation errors in extract_data_from_document."""
        tenant_id = "" if empty_tenant else "test-tenant"
        document_path = "/non/existent/path.pdf" if missing_file else self.get_test_file_path("document.pdf")

        with patch("os.path.exists", return_value=not missing_file):
            if missing_file:
                with pytest.raises(FileNotFoundException):
                    document_service.extract_data_from_document(tenant_id, document_path)
            elif empty_tenant:
                with pytest.raises(ValueError, match="Tenant ID is required"):
                    document_service.extract_data_from_document(tenant_id, document_path)
