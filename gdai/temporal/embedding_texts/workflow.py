from datetime import timedelta

from temporalio import workflow


@workflow.defn
class TextEmbeddingWorkflow:
    @workflow.run
    async def run(self, text_to_embedding: dict[str, str]) -> dict[str, list[float]]:
        text_embedded = await workflow.execute_activity(
            "embedding_texts",
            text_to_embedding,
            schedule_to_close_timeout=timedelta(seconds=30),
        )
        return text_embedded
