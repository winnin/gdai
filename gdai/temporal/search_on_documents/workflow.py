from datetime import timedelta

from temporalio import workflow

from gdai.temporal.search_on_documents.schema import SearchInput, SearchResult


@workflow.defn
class DocumentSearchWorkflow:
    @workflow.run
    async def run(self, search_input: SearchInput) -> SearchResult:
        search_results = await workflow.execute_activity("search_documents", search_input, schedule_to_close_timeout=timedelta(seconds=30))
        return f"Search completed. Found {len(search_results)} documents."
