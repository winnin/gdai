import asyncio
from datetime import timedelta

from temporalio import workflow

from gdai.temporal.embedding_chunks.schema import ChunkStoreEmbeding

with workflow.unsafe.imports_passed_through():
    from gdai.commons.config import Config


@workflow.defn
class ChunkEmbeddingWorkflow:
    @workflow.run
    async def run(self, chunk_file_path: str) -> str:
        batch_id = "chunk_embedding_workflow"
        chunks = await workflow.execute_activity("get_chunks_to_embedding", chunk_file_path, schedule_to_close_timeout=timedelta(seconds=50))
        batch_size = int(Config.embedding.BATCH_SIZE / 4)
        batches = [chunks[i : i + batch_size] for i in range(0, len(chunks), batch_size)]

        # Execute all child workflows in parallel
        tasks = []
        for idx, batch in enumerate(batches):
            input_to_embedding = {chunk["id"]: chunk["chunk"] for chunk in batch}
            tasks.append(
                workflow.execute_child_workflow(
                    "TextEmbeddingWorkflow",
                    input_to_embedding,
                    id=f"embedding_chunks_{batch_id}_{idx}",
                    task_queue="embedding-text-queue",
                )
            )
        batch_results = await asyncio.gather(*tasks)

        # Update embeddings in chunks
        for batch, batch_result in zip(batches, batch_results):
            for chunk in batch:
                if chunk["id"] in batch_result:
                    chunk["embedding"] = batch_result[chunk["id"]]
            output_file = await workflow.execute_activity(
                "create_chunkfile_with_embeddings",
                ChunkStoreEmbeding(file_path=chunk_file_path, chunks=batch),
                schedule_to_close_timeout=timedelta(seconds=50),
            )

        return output_file
