from temporalio import activity

from gdai.commons.enums import QueryStatusEnum
from gdai.commons.logger import logger
from gdai.repositories import RepositoryFactory
from gdai.repositories.models import QueryModel

from .schema import (
    Chunk,
    ChunkSearchParam,
    FormatAnswerInput,
    PromptInput,
    QueryInput,
    UpdateQueryResultInput,
)

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
        logger.info(
            f"Starting query registration for query_id: {query_param.query_id}, tenant: {query_param.tenant_id}"
        )

        await __REPOSITORY.insert_query(
            QueryModel(
                id=query_param.query_id,
                tenant_id=query_param.tenant_id,
                query=query_param.query,
                status=QueryStatusEnum.pending,
            )
        )

        logger.info(f"Query {query_param.query_id} registered successfully for tenant {query_param.tenant_id}")

    except Exception as e:
        logger.error(f"Error registering query {query_param.query_id} for tenant {query_param.tenant_id}: {e}")
        raise e


@activity.defn
async def get_chunks(search_query_param: ChunkSearchParam) -> list[Chunk]:
    try:
        logger.info(
            f"""Starting chunk search for tenant: {search_query_param.tenant_id}, limit: {search_query_param.limit}, \
                threshold: {search_query_param.similarity_threshold}"""
        )

        if search_query_param.document_ids:
            logger.debug(f"Searching within specific documents: {search_query_param.document_ids}")

        result = await __REPOSITORY.search_chunks_by_similarity_on_document_ids(
            tenant_id=search_query_param.tenant_id,
            query_vector=search_query_param.query_embedding,
            similarity_threshold=search_query_param.similarity_threshold,
            document_ids=search_query_param.document_ids,
            limit=search_query_param.limit,
        )

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

        logger.info(
            f"Found {len(chunks)} chunks matching the search criteria for tenant {search_query_param.tenant_id}"
        )
        logger.debug(f"Chunk similarities range: {[chunk.query_similarity for chunk in chunks[:5]]}")

        return chunks

    except Exception as e:
        logger.error(f"Error searching chunks for tenant {search_query_param.tenant_id}: {e}")
        raise e


@activity.defn
async def save_query_result(input: UpdateQueryResultInput) -> None:
    try:
        logger.info(f"Saving query result for query {input.query_id}, tenant {input.tenant_id}")
        logger.debug(f"Query result status: {input.status}, answer length: {len(input.answer) if input.answer else 0}")

        # update query result
        await __REPOSITORY.update_query_result(
            query_id=input.query_id,
            tenant_id=input.tenant_id,
            result=input.answer,
            status=input.status,
        )

        # link query with chunks
        if input.chunks:
            chunk_links = [(chunk.chunk_id, chunk.query_similarity) for chunk in input.chunks]
            await __REPOSITORY.insert_query_chunk_links(
                tenant_id=input.tenant_id,
                query_id=input.query_id,
                chunks_ids_with_similarity=chunk_links,
            )

            chunk_count = len(input.chunks)
            logger.info(f"Linked query {input.query_id} with {chunk_count} chunks")
        else:
            logger.warning(f"No chunks to link for query {input.query_id}")

        logger.info(f"Query result saved successfully for query {input.query_id}")

    except Exception as e:
        logger.error(f"Error saving query result for query {input.query_id}: {e}")
        raise e


@activity.defn
async def generate_prompt_from_template(prompt_input: PromptInput) -> str:
    try:
        logger.info(f"Generating prompt with {len(prompt_input.chunks)} chunks")
        logger.debug(f"Query length: {len(prompt_input.query)}")

        chunks_text = "\n\n".join([chunk.text for chunk in prompt_input.chunks])
        prompt = __PROMPT_TEMPLATE_TO_SOLVE_QUERY.format(query=prompt_input.query, chunks=chunks_text)

        logger.info(f"Generated prompt with {len(prompt)} characters")
        logger.debug(f"Total chunks text length: {len(chunks_text)}")

        return prompt

    except Exception as e:
        logger.error(f"Error generating prompt from template: {e}")
        raise e


@activity.defn
async def format_answer(format_answer_input: FormatAnswerInput) -> dict:
    try:
        logger.info(
            f"Formatting answer for query {format_answer_input.query_id}, tenant {format_answer_input.tenant_id}"
        )
        logger.debug(f"Answer length: {len(format_answer_input.llm_answer) if format_answer_input.llm_answer else 0}")
        logger.debug(f"Number of chunks: {len(format_answer_input.chunks) if format_answer_input.chunks else 0}")

        result = format_answer_input.__dict__

        logger.info(f"Answer formatted successfully for query {format_answer_input.query_id}")

        return result

    except Exception as e:
        logger.error(f"Error formatting answer for query {format_answer_input.query_id}: {e}")
        raise e
