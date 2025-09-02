from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


@workflow.defn
class TextEmbeddingWorkflow:
    @workflow.run
    async def run(self, text_to_embedding: dict[str, str]) -> dict[str, list[float]]:
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=30),  # Espera 30 segundos antes do primeiro retry
            maximum_interval=timedelta(seconds=30),  # Mantém o intervalo constante em 30 segundos
            maximum_attempts=10,  # Limita o número total de tentativas
            backoff_coefficient=1.0,  # Sem aumento exponencial (1.0 = linear)
        )
        text_embedded = await workflow.execute_activity(
            "embedding_texts",
            text_to_embedding,
            schedule_to_close_timeout=timedelta(days=1),
            retry_policy=retry_policy,
        )
        return text_embedded
