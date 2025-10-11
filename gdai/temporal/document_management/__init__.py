"""Document management workflows package."""

from .schema import (
    Chunk,
    DeleteDocumentInput,
    Document,
    DocumentStatus,
    GetDocumentChunksInput,
    GetDocumentChunksOutput,
    GetDocumentInput,
    GetDocumentStatusInput,
    ListDocumentsInput,
    ListDocumentsOutput,
)
from .workflow import (
    DeleteDocumentWorkflow,
    GetDocumentChunksWorkflow,
    GetDocumentStatusWorkflow,
    GetDocumentWorkflow,
    ListDocumentsWorkflow,
)

__all__ = [
    # Schemas
    "Chunk",
    "DeleteDocumentInput",
    "Document",
    "DocumentStatus",
    "GetDocumentChunksInput",
    "GetDocumentChunksOutput",
    "GetDocumentInput",
    "GetDocumentStatusInput",
    "ListDocumentsInput",
    "ListDocumentsOutput",
    # Workflows
    "DeleteDocumentWorkflow",
    "GetDocumentChunksWorkflow",
    "GetDocumentStatusWorkflow",
    "GetDocumentWorkflow",
    "ListDocumentsWorkflow",
]
