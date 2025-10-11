"""Exception hierarchy for GDAI application."""

from __future__ import annotations

from typing import Any


class GDAIException(Exception):
    """Base exception for all GDAI errors.

    Attributes:
        message: Human-readable error message
        code: Machine-readable error code
        details: Additional context about the error
    """

    def __init__(self, message: str, code: str, details: dict[str, Any] | None = None):
        """Initialize GDAI exception.

        Args:
            message: Human-readable error message
            code: Machine-readable error code (e.g., "DOCUMENT_NOT_FOUND")
            details: Additional context about the error
        """
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary format.

        Returns:
            dict: Exception data suitable for API responses
        """
        return {"code": self.code, "message": self.message, "details": self.details}


# Document exceptions
class DocumentError(GDAIException):
    """Base exception for document-related errors."""

    pass


class DocumentNotFoundError(DocumentError):
    """Raised when a document is not found."""

    def __init__(self, tenant_id: str, document_id: str):
        super().__init__(
            message=f"Document {document_id} not found",
            code="DOCUMENT_NOT_FOUND",
            details={"tenant_id": tenant_id, "document_id": document_id},
        )


class DocumentAlreadyExistsError(DocumentError):
    """Raised when attempting to create a document that already exists."""

    def __init__(self, tenant_id: str, document_id: str):
        super().__init__(
            message=f"Document {document_id} already exists",
            code="DOCUMENT_ALREADY_EXISTS",
            details={"tenant_id": tenant_id, "document_id": document_id},
        )


class DocumentProcessingError(DocumentError):
    """Raised when document processing fails."""

    def __init__(self, document_id: str, reason: str):
        super().__init__(
            message=f"Failed to process document {document_id}: {reason}",
            code="DOCUMENT_PROCESSING_ERROR",
            details={"document_id": document_id, "reason": reason},
        )


# Extraction exceptions
class ExtractionError(GDAIException):
    """Base exception for extraction-related errors."""

    pass


class UnsupportedDocumentTypeError(ExtractionError):
    """Raised when document type is not supported."""

    def __init__(self, document_type: str):
        super().__init__(
            message=f"Document type '{document_type}' is not supported",
            code="UNSUPPORTED_DOCUMENT_TYPE",
            details={"document_type": document_type},
        )


class ExtractionFailedError(ExtractionError):
    """Raised when extraction process fails."""

    def __init__(self, document_id: str, reason: str):
        super().__init__(
            message=f"Failed to extract document {document_id}: {reason}",
            code="EXTRACTION_FAILED",
            details={"document_id": document_id, "reason": reason},
        )


# Chunk exceptions
class ChunkError(GDAIException):
    """Base exception for chunk-related errors."""

    pass


class ChunkNotFoundError(ChunkError):
    """Raised when a chunk is not found."""

    def __init__(self, tenant_id: str, chunk_id: str):
        super().__init__(
            message=f"Chunk {chunk_id} not found",
            code="CHUNK_NOT_FOUND",
            details={"tenant_id": tenant_id, "chunk_id": chunk_id},
        )


# Query exceptions
class QueryError(GDAIException):
    """Base exception for query-related errors."""

    pass


class QueryNotFoundError(QueryError):
    """Raised when a query is not found."""

    def __init__(self, tenant_id: str, query_id: str):
        super().__init__(
            message=f"Query {query_id} not found",
            code="QUERY_NOT_FOUND",
            details={"tenant_id": tenant_id, "query_id": query_id},
        )


class QueryProcessingError(QueryError):
    """Raised when query processing fails."""

    def __init__(self, query_id: str, reason: str):
        super().__init__(
            message=f"Failed to process query {query_id}: {reason}",
            code="QUERY_PROCESSING_ERROR",
            details={"query_id": query_id, "reason": reason},
        )


# Embedding exceptions
class EmbeddingError(GDAIException):
    """Base exception for embedding-related errors."""

    pass


class EmbeddingGenerationError(EmbeddingError):
    """Raised when embedding generation fails."""

    def __init__(self, text: str, reason: str):
        super().__init__(
            message=f"Failed to generate embedding: {reason}",
            code="EMBEDDING_GENERATION_ERROR",
            details={"text_preview": text[:100], "reason": reason},
        )


# LLM exceptions
class LLMError(GDAIException):
    """Base exception for LLM-related errors."""

    pass


class LLMGenerationError(LLMError):
    """Raised when LLM text generation fails."""

    def __init__(self, prompt: str, reason: str):
        super().__init__(
            message=f"Failed to generate text: {reason}",
            code="LLM_GENERATION_ERROR",
            details={"prompt_preview": prompt[:100], "reason": reason},
        )


# Storage exceptions
class StorageError(GDAIException):
    """Base exception for storage-related errors."""

    pass


class FileNotFoundError(StorageError):
    """Raised when a file is not found in storage."""

    def __init__(self, file_path: str):
        super().__init__(
            message=f"File not found: {file_path}",
            code="FILE_NOT_FOUND",
            details={"file_path": file_path},
        )


class FileUploadError(StorageError):
    """Raised when file upload fails."""

    def __init__(self, file_name: str, reason: str):
        super().__init__(
            message=f"Failed to upload file {file_name}: {reason}",
            code="FILE_UPLOAD_ERROR",
            details={"file_name": file_name, "reason": reason},
        )


# Validation exceptions
class ValidationError(GDAIException):
    """Base exception for validation errors."""

    pass


class InvalidInputError(ValidationError):
    """Raised when input validation fails."""

    def __init__(self, field: str, reason: str):
        super().__init__(
            message=f"Invalid input for field '{field}': {reason}",
            code="INVALID_INPUT",
            details={"field": field, "reason": reason},
        )


# Authentication/Authorization exceptions
class AuthenticationError(GDAIException):
    """Base exception for authentication errors."""

    pass


class UnauthorizedError(AuthenticationError):
    """Raised when authentication fails."""

    def __init__(self, reason: str = "Invalid or missing credentials"):
        super().__init__(message=reason, code="UNAUTHORIZED", details={"reason": reason})


class ForbiddenError(GDAIException):
    """Raised when user doesn't have permission."""

    def __init__(self, resource: str, action: str):
        super().__init__(
            message=f"Permission denied for action '{action}' on resource '{resource}'",
            code="FORBIDDEN",
            details={"resource": resource, "action": action},
        )


# Workflow exceptions
class WorkflowError(GDAIException):
    """Base exception for Temporal workflow errors."""

    pass


class WorkflowExecutionError(WorkflowError):
    """Raised when workflow execution fails."""

    def __init__(self, workflow_id: str, reason: str):
        super().__init__(
            message=f"Workflow {workflow_id} execution failed: {reason}",
            code="WORKFLOW_EXECUTION_ERROR",
            details={"workflow_id": workflow_id, "reason": reason},
        )


class WorkflowNotFoundError(WorkflowError):
    """Raised when workflow is not found."""

    def __init__(self, workflow_id: str):
        super().__init__(
            message=f"Workflow {workflow_id} not found",
            code="WORKFLOW_NOT_FOUND",
            details={"workflow_id": workflow_id},
        )
