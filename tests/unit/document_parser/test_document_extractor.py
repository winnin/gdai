from __future__ import annotations

import os

import pytest

from src.actor.extractor.document_extractor import DoclingPDFExtractor


class TestParserDocumentExtractor:
    """
    Tests based on some public documents from Wikipedia stored as pdf
    """

    @pytest.fixture
    def file_path(self):
        base_path = "./tests/fixtures/document_parser/"
        return base_path

    @pytest.fixture
    def long_pdf_with_text_and_images(self, file_path):
        doc_full_path = os.path.join(
            file_path, "document_large_with_text_and_image.pdf"
        )
        return doc_full_path

    @pytest.fixture
    def regular_pdf_with_table(self, file_path):
        doc_full_path = os.path.join(file_path, "document_with_table.pdf")
        return doc_full_path

    @pytest.fixture
    def pdf_as_image(self, file_path):
        doc_full_path = os.path.join(file_path, "document_as_image.pdf")
        return doc_full_path

    @pytest.fixture(scope="class")
    def extractor(self):
        return DoclingPDFExtractor()

    def test_docling_extract_pdf_large_with_text_and_images(
        self, extractor, long_pdf_with_text_and_images
    ):
        extracted_text = extractor.extract_document_data(long_pdf_with_text_and_images)
        num_pages = len(extracted_text.texts)
        assert num_pages == 28  # 28 pages in the document

    # def test_docling_extract_pdf_with_table(self, extractor, regular_pdf_with_table):
    #    extracted_text = extractor.extract_document_data(regular_pdf_with_table)

    # def test_docling_extract_pdf_as_image():
    #     pass
