from temporalio import activity

from gdai.chunkers import ChunkerFactory
from gdai.temporal.schemas import DocumentChunk, RawDocument


class DocumentChunkerActivity:
    @activity.defn
    async def chunk(self, chunk_strategy, raw_document: RawDocument) -> list[DocumentChunk]:
        # verify chunk strategy

        _ = ChunkerFactory.get_chunker(chunker_type=chunk_strategy)

        only_text_by_page = [item[1] for item in raw_document.texts]
        raw_document.texts = self.chunker.chunk(only_text_by_page)
