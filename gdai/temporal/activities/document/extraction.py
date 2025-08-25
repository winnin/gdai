from temporalio import activity

from gdai.commons.config import Config
from gdai.commons.logger import logger
from gdai.temporal.schemas import RawDocument


class ExtractDocument:
    @activity.defn
    async def extract_document_text_activity(self, tenant_id: str, document_path: str) -> RawDocument:
        # get document extension
        document_extension = document_path.split(".")[-1].lower()

        # load de proper extractor based on the extension
        extractor = Config.extractor.get_extractor(document_extension)

        try:
            extracted_document = extractor.extract_document_data(tenant_id, document_path)
            return extracted_document
        except Exception as e:
            logger.error(f"Error extracting data from document: {e}")
            raise e
