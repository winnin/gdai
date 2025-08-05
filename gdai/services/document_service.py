from __future__ import annotations

import os

from gdai.chunkers.base_chunker import BaseChunker
from gdai.commons.enums import DocumentStatusEnum, DocumentTypeEnum
from gdai.config.logger import logger
from gdai.config.settings import Config
from gdai.extractors.base_extractor import DocumentExtractor
from gdai.extractors.exceptions import FileNotFoundException
from gdai.mappers.chunk_mapper import RawChunkerMapper
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

    def __register_document_to_be_processed_on_db(self, tenant_id: str, document_path: str) -> Document:
        """Register a document to be processed.

        Args:
            tenant_id (str): The tenant ID.
            document_path (str): The path to the document file.

        Returns:
            Document: The registered document object.
        """
        doc_extension = document_path.split(".")[-1].lower()
        if doc_extension not in DocumentTypeEnum.__members__:
            logger.error(f"Unsupported document type: {doc_extension}")
            raise ValueError(f"Unsupported document type: {doc_extension}")

        chunker_strategy = str(self.chunker)
        doc = Document(
            name=os.path.basename(document_path),
            tenant_id=tenant_id,
            status=DocumentStatusEnum.uploaded,
            type=DocumentTypeEnum[doc_extension],
            chunk_strategy=chunker_strategy,
        )

        doc = self.repository.insert_document(doc)
        return doc

    def __generate_document_chunks(self, tenant_id: str, document_id: str, document_path: str) -> list[str]:
        """Get the chunks of a document.

        Args:
            tenant_id (str): The tenant ID.
            document_path (str): The path to the document file.

        Returns:
            list[str]: The list of text chunks extracted from the document.
        """
        raw_document = self.document_extractor.extract_document_data(tenant_id, document_path)
        only_text_by_page = [item[1] for item in raw_document.texts]
        raw_document.texts = self.chunker.chunk(only_text_by_page)
        chunks = RawChunkerMapper.to_chunks(raw_document)
        for chunk in chunks:
            chunk.tenant_id = tenant_id
            chunk.document_id = document_id
        return chunks

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

        # Register the document to be processed
        doc = await self.__register_document_to_be_processed_on_db(tenant_id, document_path)

        try:
            doc.status = DocumentStatusEnum.extracting
            doc = await self.repository.update_document(doc)

            chunks = self.__generate_document_chunks(tenant_id, str(doc.id), document_path)
            chunks = await self.repository.insert_chunks(tenant_id, str(doc.id), chunks)

            doc.status = DocumentStatusEnum.extracted
            doc = await self.repository.update_document(doc)

            doc.chunks = chunks  # add chunks to the document object

            return doc
        except Exception as e:
            doc.status = DocumentStatusEnum.extraction_failed
            logger.error(f"Error extracting data from document: {e}")
            raise e


class DocumentInformationService:
    """Service for managing document information."""

    def __init__(self, repository: BaseRepository):
        """Initialize the DocumentInformationService with a repository.

        Args:
            repository (BaseRepository): The repository to use for document operations.
        """
        self.repository = repository

    async def get_all_documents(self, tenant_id: str) -> list[Document]:
        """Get all documents for a specific tenant.

        Args:
            tenant_id (str): The tenant ID.

        Returns:
            list[Document]: The list of documents for the tenant.
        """

        if not tenant_id:
            raise ValueError("Tenant ID is required")

        documents = await self.repository.get_all_documents(tenant_id)
        return documents

    async def get_document_by_id(self, tenant_id: str, document_id: str) -> Document:
        """Get a document by its ID for a specific tenant.

        Args:
            tenant_id (str): The tenant ID.
            document_id (str): The document ID.

        Returns:
            Document: The document object.

        Raises:
            ValueError: If the tenant ID or document ID is not provided.
        """

        if not tenant_id:
            raise ValueError("Tenant ID is required")
        if not document_id:
            raise ValueError("Document ID is required")

        document = await self.repository.get_document(tenant_id, document_id)
        return document
