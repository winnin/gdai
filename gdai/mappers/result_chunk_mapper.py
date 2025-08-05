from gdai.repositories.models import ChunkModel
from gdai.schemas.schemas import ResultChunk


class ResultChunkMapper:
    """Mapper for Chunk schema and ChunkModel ORM models."""

    @staticmethod
    def to_schema(chunk_model: ChunkModel, similarity: float) -> ResultChunk:
        """Convert a ChunkModel to a Chunk schema.

        Args:
            model: ChunkModel database object

        Returns:
            Chunk: The equivalent schema object
        """
        result = ResultChunk(
            chunk=chunk_model.chunk,
            type=chunk_model.type,
            similarity_score=similarity,
            page_number=chunk_model.page_number,
        )
        return result
