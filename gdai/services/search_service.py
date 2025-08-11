# The SearchService class has been moved to src/api/services/search_service.py
from __future__ import annotations

from gdai.commons.enums import QueryStatusEnum, SimilarityTypeEnum
from gdai.config.logger import logger
from gdai.embeddings import EmbeddingModel
from gdai.llms import LLMModel
from gdai.repositories import BaseRepository
from gdai.schemas import Chunk
from gdai.schemas.schemas import QueryResult, ResultChunk


class SearchService:
    """Service for handling search queries using LLM and embeddings."""

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

    def __init__(self, llm_model: LLMModel, embedding_model: EmbeddingModel, repository: BaseRepository):
        """Initialize the SearchService.

        Args:
            llm_model (LLMModel): The language model to use for answering queries.
            embedding_model: The embedding model for vector search.
            repository: The repository for database access.
        """
        self.llm_model = llm_model
        self.embedding_model = embedding_model
        self.repository = repository

    async def _generate_answer(self, query: str, chunks: list[Chunk]) -> str:
        """Generate an answer using the LLM based on the query and relevant chunks.

        Args:
            message_id (str): The ID of the message.
            query (str): The query text.
            chunks_result: The relevant document chunks.

        Returns:
            dict: The generated answer and used chunks.
        """
        # Format chunks for the prompt
        chunks_text = "\n\n".join([chunk.chunk for chunk in chunks])

        # Prepare the prompt for the LLM
        prompt = self.__PROMPT_TEMPLATE_TO_SOLVE_QUERY.format(query=query, chunks=chunks_text)

        # Get streaming response from LLM and store tokens
        answer_text = await self.llm_model.call_llm(prompt)

        if answer_text is None or "There is no relevant information" in answer_text:
            return {"msg": "There is no relevant information available."}

        return {"msg": answer_text}

    async def answer_query(self, tenant_id: str, query: str, document_ids_to_search=[], chunks_limit: int = 10) -> dict:
        """Answer a query by searching for relevant documents and generating a response.

        Args:
            tenant_id (str): The ID of the tenant.
            query (str): The query text.
            chunks_limit (int): The maximum number of chunks to use.

        Returns:
            dict: The answer to the query and the used chunks.
        """
        # insert query in database
        query_id = await self.repository.insert_query(tenant_id, query, SimilarityTypeEnum.cosine)

        # embedding query
        embedded_query = (await self.embedding_model.generate_texts_embeddings([query]))[0]
        chunks = []
        if len(document_ids_to_search) == 0:
            try:
                chunks = await self.repository.search_chunks_by_similarity(
                    tenant_id=tenant_id,
                    query_id=query_id,
                    query_vector=embedded_query,
                    similarity_threshold=0.00,
                    limit=chunks_limit,
                )
            except ValueError as e:
                logger.error(f"Error retrieving chunks for query {query_id}: {e!s}")
        else:
            try:
                chunks = await self.repository.search_chunks_by_similarity_and_document_ids(
                    tenant_id=tenant_id,
                    query_id=query_id,
                    query_vector=embedded_query,
                    document_ids=document_ids_to_search,
                    similarity_threshold=0.00,
                    limit=chunks_limit,
                )
            except ValueError as e:
                logger.error(f"Error retrieving chunks for query {query_id}: {e!s}")

        try:
            msg_result = (await self._generate_answer(query=query, chunks=chunks))["msg"]
            query_res = await self.repository.get_query(tenant_id=tenant_id, query_id=str(query_id))
            query_res.result = msg_result
            query_res.status = QueryStatusEnum.completed
            await self.repository.update_query(tenant_id=tenant_id, query=query_res)
        except Exception as e:
            logger.error(f"Error generating answer for query {query_id}: {e!s}")
            query_res = await self.repository.get_query(tenant_id=tenant_id, query_id=str(query_id))
            query_res.status = QueryStatusEnum.failed
            await self.repository.update_query(tenant_id=tenant_id, query=query_res)
            raise e

        response = QueryResult(
            query=query,
            result=msg_result,
            status=query_res.status,
            result_chunks=[
                ResultChunk(
                    chunk=chunk.chunk,
                    type=chunk.type,
                    page_number=chunk.page_number,
                    document_id=chunk.document_id,
                    similarity_score=chunk.similarity_score,
                )
                for chunk in chunks
            ],
        )

        return response
