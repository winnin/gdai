from __future__ import annotations

import os

from gdai.config.logger import logger
from gdai.config.settings import Config
from gdai.extractors.exceptions import FileNotFoundException
from gdai.extractors.pdf import PyMuPDFExtractor
from gdai.schemas import Document


class ExtractDocumentService:
    """Service for extracting text from documents."""

    def __init__(self):
        """Initialize the ExtractDocumentService with a document extractor.

        Args:
            document_extractor (DocumentExtractor): The extractor to use for document parsing.
        """

    def extract_data_from_document(self, tenant_id: str, document_path: str) -> Document:
        """Extract text from a document.

        Args:
            tenant_id (str): The tenant ID.
            document_path (str): The path to the document file.

        Returns:
            Document: The extracted document object.

        Raises:
            FileNotFoundException: If the document file does not exist.
        """
        # Check if the file exists
        if not os.path.exists(document_path):
            logger.error(f"Document file {document_path} does not exist")
            raise FileNotFoundException()

        # Check if tenant_id is provided
        if not tenant_id:
            logger.error("Tenant ID is required")
            raise ValueError("Tenant ID is required")

        # Check if the file exists
        if not os.path.exists(document_path):
            logger.error(f"Document file {document_path} does not exist")
            raise FileNotFoundError(f"Document file {document_path} does not exist")

        # Check if the file is readable
        if not os.access(document_path, os.R_OK):
            logger.error(f"Document file {document_path} is not readable")
            raise PermissionError(f"Document file {document_path} is not readable")

        # Check file size
        file_size = os.path.getsize(document_path)
        if file_size == 0:
            logger.error(f"Document file {document_path} is empty")
            raise ValueError(f"Document file {document_path} is empty")

        if file_size > Config.extractor.MAX_FILE_SIZE_MB * 1024 * 1024:  # configured limit in MB
            logger.error(f"Document file {document_path} exceeds maximum allowed size")
            raise ValueError(f"Document file {document_path} exceeds maximum allowed size")

        # Extract the document data
        document_extractor = PyMuPDFExtractor()  # TODO: must be based on the document type
        _ = document_extractor.extract_document_data(document_path)

        # document_data = document_extractor.extract_document_data(document_path)

        # chunk document_data

        # insert document into the database

        # insert chunks into the database
