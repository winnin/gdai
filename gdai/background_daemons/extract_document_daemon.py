import asyncio

from gdai.chunkers import ChunkerFactory
from gdai.config.config import Config
from gdai.config.logger import logger
from gdai.extractors import ExtractorFactory
from gdai.repositories import RepositoryFactory
from gdai.services.document_service import ExtractDocumentService


class ExtractDocumentDaemon:
    def __init__(self):
        self.repository = RepositoryFactory.get_repository()
        self.batch_size = Config.extractor.BATCH_SIZE

    async def run(self) -> None:
        """Extract text from a document and store it in the database.

        Args:
            document_data (dict): The document data containing metadata and file paths.
        """
        while True:
            try:
                logger.info("Starting a new batch document extraction ")
                documents = await self.repository.get_documents_to_extract(limit=self.batch_size)

                if len(documents) == 0 or documents is None:
                    await asyncio.sleep(5)  # waiting 5 seconds before the next batch
                    continue

                for document in documents:
                    logger.info(f"Begin extraction for document id:{document.id} - name:{document.name}")
                    tenant_id = document.tenant_id
                    document_extension = document.name.split(".")[-1].lower()
                    document_extractor = ExtractorFactory.get_extractor(extractor_type=document_extension)
                    chunker = ChunkerFactory.get_chunker(chunker_type=document.chunk_strategy)
                    extract_service = ExtractDocumentService(self.repository, document_extractor, chunker)
                    await extract_service.extract_data_from_document(tenant_id, str(document.id))
                    logger.info(f"Finishing extraction for document id:{document.id} - name:{document.name}")
                logger.info("Batch document extraction completed successfully")

            except Exception as e:
                logger.error(f"Failed to extract documents: {e!s}")
                raise
