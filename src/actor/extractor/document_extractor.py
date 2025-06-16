from __future__ import annotations

import os
from abc import ABC, abstractmethod
from collections import defaultdict

import fitz  # PyMuPDF
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, InputFormat, PdfFormatOption

from src.shared.schema import Document, Image, Table, Text


class DocumentExtractor(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def extract_document_data(document_path: str) -> dict:
        """
        Extract text from a document.
        """
        pass


class PyMuPDFExtractor(DocumentExtractor):
    """
    Extract text, tables and images from a PDF document using PyMuPDF (fitz).
    """

    def __init__(self):
        super().__init__()
        # No special initialization needed for PyMuPDF

    def extract_document_data(self, document_path: str) -> dict:
        """
        Extract content from a PDF document.
        """
        # Check if the document exists
        if not os.path.exists(document_path):
            raise ValueError(f"Document {document_path} does not exist")

        # Get the name of the document from full path
        doc_name = self._get_document_name(document_path)

        try:
            # Open the PDF document
            pdf_document = fitz.open(document_path)

            # Extract data
            dict_result = {
                "texts": self._extract_raw_text(pdf_document),
                "tables": self._extract_raw_tables(pdf_document),
                "pictures": self._extract_raw_images(pdf_document),
            }

            # Format the output to a Document object
            document = self._format_output(doc_name, dict_result)

            # Close the document
            pdf_document.close()

            return document

        except Exception as e:
            print(f"Error extracting data from {doc_name}: {e!s}")
            raise

    def _get_document_name(self, document_path: str) -> str:
        """
        Get the document name from the document path.
        """
        file_name = os.path.basename(document_path)
        return file_name

    def _join_paragraphs_between_pages(self, text_data: list[dict]) -> list:
        """
        Join paragraphs that are split between pages.
        This is a simple heuristic that checks if the last character of the previous page
        is a punctuation mark and the first character of the next page is not.
        """
        if not text_data:
            return text_data

        for i in range(len(text_data) - 1):
            page_current_text = text_data[i]["page_number"]
            current_text = text_data[i]["text"]

            next_text = text_data[i + 1]["text"]
            page_next_text = text_data[i + 1]["page_number"]

            next_text_list_paragraphs = next_text.split("\n\n")

            if next_text_list_paragraphs[0][
                0
            ].isupper():  # if first character is uppercase
                next_text = "\n\n".join(next_text_list_paragraphs)
            else:
                current_text += f"\n{next_text_list_paragraphs[0]}"
                next_text = (
                    "\n\n".join(next_text_list_paragraphs[1:])
                    if len(next_text_list_paragraphs) > 1
                    else ""
                )

            text_data[i] = {"page_number": page_current_text, "text": current_text}
            text_data[i + 1] = {"page_number": page_next_text, "text": next_text}

        return text_data

    def _extract_raw_text(self, pdf_document) -> list[dict]:
        """
        Extract raw text from PDF using PyMuPDF.
        Returns list of text items with page information.
        """
        text_data = []

        for page_num, page in enumerate(pdf_document):
            text = page.get_text()
            text = text.strip()  # Remove leading/trailing whitespace
            text = text.replace(".\n", ".$$$$$")
            text = text.replace("\n\n", "$$$$$")
            text = text.replace(". \n", "$$$$$")  # Replace newlines with spaces
            text = text.replace("$$$$$", "\n\n")
            text = text.replace("\n \n", "\n")  # Remove double newlines

            text_data
            if text:  # Only add if there's actual text content
                text_data.append({"text": text, "page_number": page_num + 1})
        text_data = self._join_paragraphs_between_pages(text_data)
        return text_data

    def _extract_raw_tables(self, pdf_document) -> list:
        """
        Extract raw table data from PDF.
        Note: Basic table detection with PyMuPDF is limited.
        For production use, consider adding tabula-py or camelot-py integration.
        """
        # Basic implementation - in real scenarios this would be more complex
        tables = []
        return tables

    def _extract_raw_images(self, pdf_document) -> list:
        """
        Extract raw image data from PDF.
        """
        images = []

        return images

    def _format_output(self, doc_name: str, dict_result: dict) -> Document:
        """
        Format the output to a Document object.
        """
        # Extract tables, images and text
        tables = self._format_table_data(dict_result["tables"])
        images = self._format_images_data(dict_result["pictures"])
        pages_text = self._format_text_data(dict_result["texts"])

        # Create a Document object
        doc = Document(
            doc_name=doc_name,
            texts=pages_text,
            tables=tables,
            images=images,
        )
        return doc

    def _format_table_data(self, raw_result) -> list[Table]:
        """
        Convert raw table data to Table objects.
        """
        # Placeholder implementation - would need to be expanded
        # for actual table extraction
        if not raw_result or len(raw_result) == 0:
            return None

        tables = []
        for table_data in raw_result:
            tables.append(
                Table(
                    page=table_data["page_num"],
                    content="Table content would be processed here",
                )
            )
        return tables

    def _format_images_data(self, raw_result) -> list[Image]:
        """
        Convert raw image data to Image objects.
        """
        if not raw_result or len(raw_result) == 0:
            return None

        images = []
        for img_data in raw_result:
            images.append(
                Image(
                    page=img_data["page_num"],
                    format=img_data["format"],
                    data=img_data["data"],
                )
            )
        return images

    def _format_text_data(self, text_result) -> list[Text]:
        """
        Convert raw text data to Text objects organized by page.
        """
        pages = [
            Text(page=page_data["page_number"], text=page_data["text"])
            for page_data in text_result
        ]
        return pages


class DoclingPDFExtractor(DocumentExtractor):
    """
    Extract text from a document using Docling.
    """

    def __init__(self):
        super().__init__()
        self.docling_extractor_without_ocr = self._generate_docling_pdf_extractor(
            use_ocr=False
        )
        self.docling_extractor_with_ocr = self._generate_docling_pdf_extractor(
            use_ocr=True
        )

    def extract_document_data(self, document_path: str) -> dict:
        """
        Extract text from a document.
        """
        # check if the document exists
        if not os.path.exists(document_path):
            raise ValueError(f"Document {document_path} does not exist")

        # get the name of the document from full path
        doc_name = self._get_document_name(document_path)

        # first try to extract text without OCR
        print(f"Extracting document {doc_name} without OCR...")
        result = self.docling_extractor_without_ocr.convert(document_path)
        dict_result = result.document.export_to_dict()

        # if method without ocr fails, try with ocr
        if len(dict_result["texts"]) == 0:
            print(f"No text found in {doc_name} without OCR, trying with OCR...")
            result = self.docling_extractor_with_ocr.convert(document_path)
            dict_result = result.document.export_to_dict()

        # format the output to a Document object
        document = self._format_output(doc_name, dict_result)
        return document

    def _get_document_name(self, document_path: str) -> str:
        """
        Get the document name from the document path.
        """
        file_name = os.path.basename(document_path)
        return file_name

    def _generate_docling_pdf_extractor(self, use_ocr: bool = False) -> Document:
        """
        Generate a Docling PDF extractor with the specified options.
        """
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = use_ocr  # pick what you need
        pipeline_options.generate_page_images = True
        pipeline_options.do_table_structure = True  # pick what you need
        docling_extractor = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )  # switch to beta PDF backend
            }
        )
        return docling_extractor

    def _format_output(self, doc_name: str, dict_result: dict) -> Document:
        """
        Format the output to a Document object.
        """
        # extract tables, images and text
        tables = self._extract_tables(dict_result["tables"])
        images = self._extract_images(dict_result["pictures"])
        pages_text = self._extract_text(dict_result["texts"])

        # create a Document object
        doc = Document(
            doc_name=doc_name,
            texts=pages_text,
            tables=tables,
            images=images,
        )
        return doc

    def _extract_tables(self, raw_result) -> list[Table]:
        return None

    def _extract_images(self, raw_result) -> list[Image]:
        return None

    def _extract_text(self, text_result) -> list[Text]:
        # extract text from docling result to a dictionary
        text_found = [
            (text_item["prov"][0]["page_no"], text_item["text"])
            for text_item in text_result
        ]

        # group text by page number
        page_data = defaultdict(str)
        for page_number, page_text in text_found:
            page_data[page_number] += (
                (" " + page_text) if page_data[page_number] else page_text
            )
        # create a list of Page objects
        pages = [Text(page=page, text=text) for page, text in page_data.items()]
        return pages
