import json

import aiofiles
from aiopath import AsyncPath
from temporalio import activity

from gdai.temporal.embedding_chunks.schema import ChunkStoreEmbeding


@activity.defn
async def get_chunks_to_embedding(file_path: str) -> list[dict]:
    async with aiofiles.open(file_path) as f:
        chunks = await f.read()
    return json.loads(chunks)


@activity.defn
async def create_chunkfile_with_embeddings(input: ChunkStoreEmbeding) -> None:
    output_file = input.file_path.replace(".json", "_with_embeddings.json")
    chunks = input.chunks
    file_exists = await AsyncPath(output_file).exists()
    existing_chunks = None
    if file_exists:
        async with aiofiles.open(output_file) as f:
            existing_chunks = json.loads(await f.read())
    if existing_chunks:
        chunks = chunks + existing_chunks
    async with aiofiles.open(output_file, "w") as f:
        await f.write(json.dumps(chunks, indent=2))
    return output_file
