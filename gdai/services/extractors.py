"""Document extraction services.

This module provides document data extraction functionality for various formats.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import pymupdf

from gdai.commons.logger import logger


class DocumentExtractor(ABC):
    """Base class for document extractors."""

    def __init__(self):
        pass

    @abstractmethod
    def extract_document_data(self, document_path: str) -> dict:
        """Extract text from a document."""
        pass


class PDFExtractor(DocumentExtractor):
    """Extract text, tables and images from a PDF document using PyMuPDF."""

    def __init__(self):
        super().__init__()

    def extract_document_data(self, document_path: str) -> dict:
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
            result = {"texts": texts, "tables": tables, "images": images}

            return result

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


class ExtractorFactory:
    """Factory class to create extractor based on the type."""

    @staticmethod
    def get_extractor(extractor_type: str):
        """Get an extractor instance based on the type."""
        if extractor_type == "pdf":
            return PDFExtractor()
        if extractor_type == "ppt":
            # Placeholder for PPT extractor, implement as needed
            raise NotImplementedError("PPT extractor is not implemented yet.")
        else:
            raise ValueError(f"Unknown extractor type: {extractor_type}")
