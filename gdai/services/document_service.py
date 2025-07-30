from __future__ import annotations

import os

from gdai.chunkers.base_chunker import BaseChunker
from gdai.config.logger import logger
from gdai.config.settings import Config
from gdai.extractors.base_extractor import DocumentExtractor
from gdai.extractors.exceptions import FileNotFoundException
from gdai.mappers import RawDocumentMapper
from gdai.repositories.base_repository import BaseRepository
from gdai.schemas import Document


class ExtractDocumentService:
    """Service for extracting text from documents."""

    def __init__(self, repository: BaseRepository, document_extractor: DocumentExtractor, chunker: BaseChunker):
        """Initialize the ExtractDocumentService with a document extractor.

        Args:
            document_extractor (DocumentExtractor): The extractor to use for document parsing.
            chunker (BaseChunker): The chunker to use for text chunking.
        """
        self.repository = repository
        self.document_extractor = document_extractor
        self.chunker = chunker

    async def extract_data_from_document(self, tenant_id: str, document_path: str) -> Document:
        """Extract text from a document.

        Args:
            tenant_id (str): The tenant ID.
            document_path (str): The path to the document file.

        Returns:
            Document: The extracted document object.

        Raises:
            FileNotFoundException: If the document file does not exist.
        """

        # Validate the input
        self.__validate_input(tenant_id, document_path)

        raw_document = self.document_extractor.extract_document_data(tenant_id, document_path)

        # Chunk document
        only_text_by_page = [item[1] for item in raw_document.texts]
        raw_document.texts = self.chunker.chunk(only_text_by_page)
        document = RawDocumentMapper.to_document(raw_document)
        document = await self.repository.insert_document_and_chunks(document)
        return document

    def __validate_input(self, tenant_id: str, document_path: str) -> None:
        """Validate the document file.

        Args:
            document_path (str): The path to the document file.

        Raises:
            FileNotFoundException: If the document file does not exist.
            PermissionError: If the document file is not readable.
            ValueError: If the document file is empty or exceeds maximum size.
        """

        # Check if the file exists
        if not os.path.exists(document_path):
            logger.error(f"Document file {document_path} does not exist")
            raise FileNotFoundException()

        # Check if tenant_id is provided
        if not tenant_id:
            logger.error("Tenant ID is required")
            raise ValueError("Tenant ID is required")

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
