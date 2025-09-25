import json

import aiofiles
from aiopath import AsyncPath
from temporalio import activity

from gdai.commons.logger import logger
from gdai.temporal.embedding_chunks.schema import ChunkStoreEmbeding


@activity.defn
async def get_chunks_to_embedding(file_path: str) -> list[dict]:
    try:
        logger.info(f"Loading chunks from file: {file_path}")
        async with aiofiles.open(file_path) as f:
            chunks = await f.read()

        chunks_data = json.loads(chunks)
        logger.info(f"Successfully loaded {len(chunks_data)} chunks from {file_path}")
        return chunks_data

    except Exception as e:
        logger.error(f"Error loading chunks from file {file_path}: {e}")
        raise


@activity.defn
async def create_chunkfile_with_embeddings(input: ChunkStoreEmbeding) -> str:
    try:
        output_file = input.file_path.replace(".json", "_with_embeddings.json")
        chunks = input.chunks

        logger.info(f"Creating chunk file with embeddings: {output_file}")
        logger.debug(f"Processing {len(chunks)} chunks for embedding storage")

        file_exists = await AsyncPath(output_file).exists()
        existing_chunks = None

        if file_exists:
            logger.debug(f"Output file already exists, loading existing chunks: {output_file}")
            async with aiofiles.open(output_file) as f:
                existing_chunks = json.loads(await f.read())

        if existing_chunks:
            chunks = chunks + existing_chunks
            logger.debug(f"Merged with {len(existing_chunks)} existing chunks, total: {len(chunks)} chunks")

        async with aiofiles.open(output_file, "w") as f:
            await f.write(json.dumps(chunks, indent=2))

        logger.info(f"Successfully created chunk file with embeddings: {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Error creating chunk file with embeddings for {input.file_path}: {e}")
        raise
