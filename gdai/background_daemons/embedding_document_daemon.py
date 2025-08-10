import asyncio

from gdai.commons.enums import DocumentStatusEnum
from gdai.config.logger import logger
from gdai.config.settings import Config
from gdai.embeddings import EmbeddingFactory
from gdai.repositories import RepositoryFactory
from gdai.services.embedding_service import EmbeddingBatchService


class EmbeddingDocumentDaemon:
    def __init__(self):
        self.batch_size = Config.embedding.BATCH_SIZE
        self.repository = RepositoryFactory.get_repository()

    async def run(self) -> None:
        """Embed chunks that are not embedded yet."""
        self.embedding_model = await EmbeddingFactory.get_embedding()
        self.embedding_service = EmbeddingBatchService(self.embedding_model, self.repository)

        while True:
            try:
                logger.info("Starting a new batch document embedding ")
                document = await self.repository.get_documents_to_embed()
                if document is not None:
                    chunks = await self.repository.get_chunks(document.tenant_id, str(document.id))
                    chunks = [chunk for chunk in chunks if chunk.embedding is None]  # to embed only chunks without embedding
                    if not chunks:
                        logger.info(f"No chunks to embed for document id: {document.id} - name: {document.name}")
                        document.status = DocumentStatusEnum.processed
                        await self.repository.update_document(document.tenant_id, document)
                        continue

                    for i in range(0, len(chunks), self.batch_size + 1):
                        batch = chunks[i : i + self.batch_size]
                        await self.embedding_service.embed_chunks(document.tenant_id, batch)

                if not document:  # No documents or chunks to process wait 3 second
                    await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"Failed to embed documents: {document.id} {e!s}")
                raise
