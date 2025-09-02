import json
import os

from temporalio import activity

from gdai.temporal.embedding_chunks.schema import ChunkStoreEmbeding


@activity.defn
async def get_chunks_to_embedding(file_path: str) -> list[dict]:
    with open(file_path) as f:
        chunks = json.load(f)
    return chunks


@activity.defn
async def create_chunkfile_with_embeddings(input: ChunkStoreEmbeding) -> None:
    output_file = input.file_path.replace(".json", "_with_embeddings.json")
    chunks = input.chunks
    file_exists = os.path.exists(output_file)
    existing_chunks = None
    if file_exists:
        with open(output_file) as f:
            existing_chunks = json.load(f)
    if existing_chunks:
        chunks = chunks + existing_chunks
    with open(output_file, "w") as f:
        f.write(json.dumps(chunks, indent=2))
    return output_file
