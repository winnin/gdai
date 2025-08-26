import os

from temporalio import activity

from gdai.commons.config import Config
from gdai.commons.logger import logger
from gdai.temporal.schemas import RawDocument


class DocumentValidatorActivity:
    @activity.defn
    async def validate(self, tenant_id: str, chunk_strategy: str, document_path: str) -> RawDocument:
        # validate tenant_id
        if not tenant_id or not isinstance(tenant_id, str):
            logger.error("Invalid tenant_id provided")
            raise ValueError("Invalid tenant_id provided")

        # validate chunk strategy
        if chunk_strategy not in Config.chunker.SUPPORTED_STRATEGIES:
            logger.error(f"Unsupported chunk strategy: {chunk_strategy}")
            raise ValueError(f"Unsupported chunk strategy: {chunk_strategy}")

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
