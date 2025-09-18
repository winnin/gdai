import uuid

from temporalio import activity

from gdai.repositories import RepositoryFactory

from .schema import Chunk


class SearchActivity:
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

    def __init__(self):
        self._repository = RepositoryFactory.get_repository()

    @activity.defn
    async def get_chunks(
        self,
        query_embedding: list[float],
        tenant_id: str,
        limit: int,
        similarity_threshold: float,
        document_ids: list[str],
    ) -> list[Chunk]:
        # Implementação de busca de chunks
        result = await self._repository.search_similar_chunks(
            tenant_id=tenant_id,
            query_id=str(uuid.uuid4()),
            query_vector=query_embedding,
            similarity_threshold=similarity_threshold,
            document_ids=document_ids,
            limit=limit,
        )

        chunks = [
            Chunk(
                chunk_id=chunk.chunk_id,
                type=str(chunk.type),
                text=chunk.chunk,
                document_id=str(chunk.document_id),
                page_number=chunk.page_number,
                query_similarity=similarity,
            )
            for chunk, similarity in result
        ]

        return chunks

    @activity.defn
    async def generate_prompt_from_template(self, query: str, chunks: list[Chunk]) -> str:
        chunks_text = "\n".join(
            [
                f"Chunk {chunk.chunk_id} (Document {chunk.document_id}, Page {chunk.page_number}): {chunk.text}"
                for chunk in chunks
            ]
        )
        prompt = self.__PROMPT_TEMPLATE_TO_SOLVE_QUERY.format(query=query, chunks=chunks_text)
        return prompt
