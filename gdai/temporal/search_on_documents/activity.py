from temporalio import activity

from gdai.commons.enums import QueryStatusEnum
from gdai.repositories import RepositoryFactory
from gdai.repositories.models import QueryModel

from .schema import Chunk, PromptInput, QueryInput, SearchQueryParam

__PROMPT_TEMPLATE_TO_SOLVE_QUERY = """
    You are an AI assistant that helps users find relevant information in documents.
    You will receive a query and a list of document chunks. Your task is to:

    1. Analyze the query and identify the key information needed.
    2. Evaluate which document chunks are most relevant to the query.
    3. Return a concise and accurate answer based ONLY on the relevant chunks.

    Rules:
    - Use only the information provided in the document chunks.
    - If no chunks are relevant, respond with "There is no relevant information available."
    - Keep the answer clear and concise, but ensure it fully addresses the query.
    - Do not add explanations, introductions, or notes—just the direct answer.
    - Answer always in the language of the query.

    Input:
    Query: {query}
    Document Chunks: {chunks}

    Answer:

"""

__REPOSITORY = RepositoryFactory.get_repository()


@activity.defn
async def register_query(query_param: QueryInput) -> None:
    try:
        await __REPOSITORY.insert_query(
            QueryModel(
                id=query_param.query_id,
                tenant_id=query_param.tenant_id,
                query=query_param.query,
                status=QueryStatusEnum.pending,
            )
        )
    except Exception as e:
        print(e)


@activity.defn
async def get_chunks(search_query_param: SearchQueryParam) -> list[Chunk]:
    # Implementação de busca de chunks
    try:
        result = await __REPOSITORY.search_chunks_by_similarity_on_document_ids(
            tenant_id=search_query_param.tenant_id,
            query_vector=search_query_param.query_embedding,
            similarity_threshold=search_query_param.similarity_threshold,
            document_ids=search_query_param.document_ids,
            limit=search_query_param.limit,
        )

        # return chunks
        chunks = [
            Chunk(
                chunk_id=str(chunk.id),
                type=str(chunk.type),
                text=chunk.chunk,
                document_id=str(chunk.document_id),
                page_number=chunk.page_number,
                query_similarity=similarity,
            )
            for chunk, similarity in result
        ]

        return chunks
    except Exception as e:
        print(e)


@activity.defn
async def save_query_result(
    query_id: str,
    tenant_id: str,
    answer: str,
    status: QueryStatusEnum = QueryStatusEnum.completed,
) -> None:
    try:
        await __REPOSITORY.update_query_result(
            query_id=query_id,
            tenant_id=tenant_id,
            result=answer,
            status=status,
        )

        # add relation between query and chunks instead of doing it in search_chunks_by_similarity_on_document_ids
        # chunk_ids_similarities = {str(chunk.id): similarity for chunk, similarity in result}
        # await __REPOSITORY.insert_query_chunk_links(
        #     query_id=search_query_param.query_id,
        #     tenant_id=search_query_param.tenant_id,
        #     chunks=chunk_ids_similarities,
        # )

    except Exception as e:
        print(e)


@activity.defn
async def generate_prompt_from_template(prompt_input: PromptInput) -> str:
    chunks_text = "\n\n".join([chunk.text for chunk in prompt_input.chunks])
    prompt = __PROMPT_TEMPLATE_TO_SOLVE_QUERY.format(query=prompt_input.query, chunks=chunks_text)
    return prompt
