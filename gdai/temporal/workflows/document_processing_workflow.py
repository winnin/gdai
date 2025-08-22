from datetime import timedelta

from temporalio import workflow


@workflow.defn
class DocumentProcessingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        await workflow.execute_activity("validate", name, schedule_to_close_timeout=timedelta(seconds=10))
        await workflow.execute_activity("extract", name, schedule_to_close_timeout=timedelta(seconds=10))
        await workflow.execute_activity("chunking", name, schedule_to_close_timeout=timedelta(seconds=10))
        await workflow.execute_activity("store", name, schedule_to_close_timeout=timedelta(seconds=10))
        return f"Document {name} processed successfully"
