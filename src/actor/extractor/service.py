from __future__ import annotations

import os
import uuid

from src.actor.extractor.document_extractor import DocumentExtractor
from src.actor.extractor.exceptions import FileNotFoundException
from src.shared.schema import Document


class ExtractDocumentService:
    """
    Service for extracting text from documents.
    """

    def __init__(self, document_extractor: DocumentExtractor):
        """
        Initialize the ExtractDocumentService with a document extractor.

        Args:
            document_extractor (DocumentExtractor): The extractor to use for document parsing.
        """
        self.document_extractor = document_extractor

    def extract_data_from_document(
        self, tenant_id: str, document_path: str
    ) -> Document:
        """
        Extract text from a document.

        Args:
            tenant_id (str): The tenant ID.
            document_path (str): The path to the document file.
        Returns:
            Document: The extracted document object.
        Raises:
            FileNotFoundException: If the document file does not exist.
        """
        if not os.path.exists(document_path):
            raise FileNotFoundException()

        document = self.document_extractor.extract_document_data(document_path)
        document.tenant_id = tenant_id
        document.doc_id = str(uuid.uuid4())
        return document
