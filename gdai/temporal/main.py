import asyncio

from gdai.temporal.embedding_chunks.worker import main as main_embedding_chunks
from gdai.temporal.embedding_texts.worker import main as main_text_embedding
from gdai.temporal.extract_document.worker import main as main_extract_document


async def main():
    await asyncio.gather(main_text_embedding(), main_extract_document(), main_embedding_chunks())


if __name__ == "__main__":
    asyncio.run(main())
