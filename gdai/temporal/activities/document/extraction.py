import os

from temporalio import activity

from gdai.commons.config import Config
from gdai.commons.logger import logger
from gdai.temporal.schemas import RawDocument


class ExtractDocument:
    @staticmethod
    @activity.defn
    async def extract_document_text_activity(tenant_id: str, document_path: str) -> RawDocument:
        # check if document exists
        if not os.path.exists(document_path):
            logger.error(f"Document file does not exist: {document_path}")
            raise FileNotFoundError(f"Document file does not exist: {document_path}")

        # check if document is readable
        if not os.access(document_path, os.R_OK):
            logger.error(f"Document file is not readable: {document_path}")
            raise PermissionError(f"Document file is not readable: {document_path}")

        # check if document max size is not exceeded
        file_size = os.path.getsize(document_path)

        # check if document is empty
        if file_size == 0:
            logger.error(f"Document file is empty: {document_path}")
            raise ValueError(f"Document file is empty: {document_path}")

        # check if document exceeds maximum size
        if file_size > Config.extractor.MAX_FILE_SIZE_MB * 1024 * 1024:  # configured limit in MB
            logger.error(f"Document file {document_path} exceeds maximum allowed size")
            raise ValueError(f"Document file {document_path} exceeds maximum allowed size")

        document_extension = document_path.split(".")[-1].lower()
        if document_extension not in Config.extractor.SUPPORTED_EXTENSIONS:  # TODO: implement this
            logger.error(f"Unsupported document type: {document_extension}")
            raise ValueError(f"Unsupported document type: {document_extension}")

        # load de proper extractor based on the extension
        extractor = Config.extractor.get_extractor(document_extension)

        if not extractor:
            logger.error(f"No extractor found for document type: {document_extension}")
            raise ValueError(f"No extractor found for document type: {document_extension}")
        # extract text from the document
        try:
            extracted_document = extractor.extract_document_data(tenant_id, document_path)
            return extracted_document
        except Exception as e:
            logger.error(f"Error extracting data from document: {e}")
            raise e
