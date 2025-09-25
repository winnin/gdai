from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


@workflow.defn
class TextEmbeddingWorkflow:
    @workflow.run
    async def run(self, text_to_embedding: dict[str, str]) -> dict[str, list[float]]:
        try:
            workflow.logger.info(f"Starting TextEmbeddingWorkflow for {len(text_to_embedding)} texts")
            workflow.logger.debug(f"Text IDs: {list(text_to_embedding.keys())}")

            retry_policy = RetryPolicy(
                initial_interval=timedelta(seconds=15),  # wait 15 seconds before the first retry
                maximum_interval=timedelta(seconds=15),  # keep the interval constant at 15 seconds
                maximum_attempts=5,  # limit the total number of attempts
                backoff_coefficient=1.0,  # no exponential increase (1.0 = linear)
            )

            workflow.logger.info("Executing text embedding activity")
            text_embedded = await workflow.execute_activity(
                "embedding_texts",
                text_to_embedding,
                schedule_to_close_timeout=timedelta(days=1),
                retry_policy=retry_policy,
            )

            workflow.logger.info(f"TextEmbeddingWorkflow completed successfully for {len(text_embedded)} texts")
            return text_embedded

        except Exception as e:
            workflow.logger.error(f"TextEmbeddingWorkflow failed: {e}")
            raise
