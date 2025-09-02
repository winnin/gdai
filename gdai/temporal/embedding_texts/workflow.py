from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


@workflow.defn
class TextEmbeddingWorkflow:
    @workflow.run
    async def run(self, text_to_embedding: dict[str, str]) -> dict[str, list[float]]:
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=15),  # wait 30 seconds before the first retry
            maximum_interval=timedelta(seconds=15),  # keep the interval constant at 30 seconds
            maximum_attempts=5,  # limit the total number of attempts
            backoff_coefficient=1.0,  # no exponential increase (1.0 = linear)
        )
        text_embedded = await workflow.execute_activity(
            "embedding_texts",
            text_to_embedding,
            schedule_to_close_timeout=timedelta(days=1),
            retry_policy=retry_policy,
        )
        return text_embedded
