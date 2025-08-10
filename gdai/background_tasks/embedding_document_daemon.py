import asyncio

from gdai.config.logger import logger


async def embedding_chunks():
    while True:
        logger.debug("EMBEDDING CHUNKS")
        await asyncio.sleep(4)
