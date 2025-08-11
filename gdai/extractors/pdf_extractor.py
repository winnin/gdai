from __future__ import annotations

import pymupdf

from gdai.commons.enums import DocumentTypeEnum
from gdai.config import logger
from gdai.extractors.base_extractor import DocumentExtractor
from gdai.schemas import RawDocument


class PDFExtractor(DocumentExtractor):
    """Extract text, tables and images from a PDF document using PyMuPDF."""

    def __init__(self):
        super().__init__()

    def extract_document_data(self, tenant_id: str, document_path: str) -> RawDocument:
        """Extract text, tables, and images from a PDF document."""
        try:
            # Open the PDF document
            pdf_document = pymupdf.open(document_path)

            # Extract raw text, tables, and images
            texts = self._extract_raw_text(pdf_document)
            tables = self._extract_raw_tables(pdf_document)
            images = self._extract_raw_images(pdf_document)

            # Close the document
            pdf_document.close()
            # Create a RawDocument instance with the extracted data
            raw_document = RawDocument(
                name=document_path.split("/")[-1],
                path=document_path,
                tenant_id=tenant_id,
                type=DocumentTypeEnum.pdf,
                texts=texts,
                tables=tables,
                images=images,
            )

            return raw_document

        except Exception as e:
            logger.error(f"Error extracting data from {document_path}: {e!s}")
            raise

    def _extract_raw_text(self, pdf_document) -> list[tuple[int, str]]:
        """Extract raw text from PDF using PyMuPDF.
        Returns list of text items with page information.
        """
        text_data: list = []

        for page_num, page in enumerate(pdf_document):
            text = page.get_text()
            text = text.strip()  # Remove leading/trailing whitespace

            if text:  # Only add if there's actual text content
                text_data.append((page_num + 1, text))

        return text_data

    def _extract_raw_tables(self, pdf_document) -> list[tuple[int, str]]:  # noqa: ARG002
        """Extract raw table data from PDF.
        Note: Basic table detection with PyMuPDF is limited.
        For production use, consider adding tabula-py or camelot-py integration.
        """
        tables: list = []
        # TODO: Implement table extraction logic
        return tables

    def _extract_raw_images(self, pdf_document) -> list[tuple[int, str]]:  # noqa: ARG002
        """Extract raw image data from PDF."""
        images: list = []
        # TODO: Implement image extraction logic
        return images
