"""Domain models (DTOs) for GDAI application."""

from .chunk import ChunkDTO, ChunkWithEmbeddingDTO
from .document import DocumentCreateDTO, DocumentDTO, DocumentStatusDTO
from .query import QueryCreateDTO, QueryDTO, QueryResultDTO

__all__ = [
    "ChunkDTO",
    "ChunkWithEmbeddingDTO",
    "DocumentCreateDTO",
    "DocumentDTO",
    "DocumentStatusDTO",
    "QueryCreateDTO",
    "QueryDTO",
    "QueryResultDTO",
]
