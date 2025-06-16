from __future__ import annotations

import pytest
from dotenv import load_dotenv

from src.actor.extractor.document_extractor import DoclingPDFExtractor
from src.actor.extractor.service import ExtractDocumentService

load_dotenv(override=True)


class TestParserService:
    @pytest.fixture
    def file_path(self):
        base_path = "./tests/fixtures/document_parser/"
        return base_path

    @pytest.fixture
    def long_pdf_with_text_and_images(self, file_path):
        file_name = "document_large_with_text_and_image.pdf"
        return file_name

    @pytest.fixture(scope="class")
    def extractor(self):
        document_extractor = DoclingPDFExtractor()
        return document_extractor

    def test_extract_document(
        self, extractor, file_path, long_pdf_with_text_and_images
    ):
        fake_tenant_id = "abcdefg_1"
        service = ExtractDocumentService(
            document_folder_path=file_path, document_extractor=extractor
        )
        document = service.extract_data_from_document(
            fake_tenant_id, long_pdf_with_text_and_images
        )
        assert len(document.texts) == 28
        assert document.tenant_id == fake_tenant_id
