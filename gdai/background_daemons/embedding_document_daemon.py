import asyncio

from gdai.commons.enums import DocumentStatusEnum
from gdai.config.config import Config
from gdai.config.logger import logger
from gdai.embeddings import EmbeddingFactory
from gdai.repositories import RepositoryFactory
from gdai.services.embedding_service import EmbeddingDocumentChunksService


class EmbeddingDocumentDaemon:
    def __init__(self):
        self.batch_size = Config.embedding.BATCH_SIZE
        self.repository = RepositoryFactory.get_repository()

    async def run(self) -> None:
        """Embed chunks that are not embedded yet."""
        self.embedding_model = await EmbeddingFactory.get_embedding()
        self.embedding_service = EmbeddingDocumentChunksService(self.embedding_model, self.repository)

        while True:
            try:
                logger.info("Starting a new document embedding ")
                document = await self.repository.get_document_to_embed()
                if document is not None:
                    logger.info(f"Begin embedding for document id:{document.id} - name:{document.name}")
                    document.status = DocumentStatusEnum.embedding
                    await self.repository.update_document(document.tenant_id, document)
                    await self.embedding_service.embed_document_chunks(document.tenant_id, str(document.id))

                if not document:  # No documents or chunks to process wait 3 second
                    await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Failed to embed documents: {document.id} {e!s}")
                raise
