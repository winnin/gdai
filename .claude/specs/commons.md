# Commons - Shared Components

This module contains shared utilities, configuration, enums, exceptions, and logging used across the entire GDAI project.

## Location

`gdai/commons/`

## Components

### settings.py - Configuration Management

Modern Pydantic Settings-based configuration system that replaced the legacy `config.py`.

#### DatabaseSettings

PostgreSQL database configuration with connection pooling.

```python
class DatabaseSettings(BaseSettings):
    database: str
    pgvector_user: str
    pgvector_password: str
    pgvector_database: str
    pgvector_host: str
    pgvector_port: int
    pgvector_min_pool_connections: int
    pgvector_max_pool_connections: int
```

**Methods:**

- `validate_pool_size()` - Validates min/max pool size configuration
- `get_url()` - Returns PostgreSQL connection URL

**Environment Variables:**

- `DATABASE` - Database type (default: "pgvector")
- `PGVECTOR_USER` - Database user
- `PGVECTOR_PASSWORD` - Database password
- `PGVECTOR_DATABASE` - Database name
- `PGVECTOR_HOST` - Database host
- `PGVECTOR_PORT` - Database port
- `PGVECTOR_MIN_POOL_CONNECTIONS` - Minimum pool size
- `PGVECTOR_MAX_POOL_CONNECTIONS` - Maximum pool size

#### S3Settings

S3/MinIO object storage configuration.

```python
class S3Settings(BaseSettings):
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    s3_region: str
    s3_use_ssl: bool
```

**Environment Variables:**

- `S3_ENDPOINT` - S3 endpoint URL
- `S3_ACCESS_KEY` - S3 access key
- `S3_SECRET_KEY` - S3 secret key
- `S3_BUCKET` - S3 bucket name
- `S3_REGION` - S3 region
- `S3_USE_SSL` - Use SSL for S3 connections

#### EmbeddingSettings

Text embedding model configuration (Cohere).

```python
class EmbeddingSettings(BaseSettings):
    embedding_model: str
    embedding_api_key: str
    embedding_dimension: int
    embedding_batch_size: int
    embedding_max_text_size: int
    embedding_max_retries: int
```

**Methods:**

- `validate_dimension()` - Validates embedding dimension is positive

**Environment Variables:**

- `EMBEDDING_MODEL` - Model identifier (e.g., "cohere/embed-v4.0")
- `EMBEDDING_API_KEY` - API key for embedding service
- `EMBEDDING_DIMENSION` - Vector dimension (default: 1536)
- `EMBEDDING_BATCH_SIZE` - Batch size for embedding generation
- `EMBEDDING_MAX_TEXT_SIZE` - Maximum text size per embedding
- `EMBEDDING_MAX_RETRIES` - Max retry attempts for API calls

#### LLMSettings

Language model configuration (OpenAI).

```python
class LLMSettings(BaseSettings):
    llm_model: str
    llm_api_key: str
    llm_max_tokens: int
    llm_temperature: float
```

**Methods:**

- `validate_temperature()` - Validates temperature is between 0 and 2

**Environment Variables:**

- `LLM_MODEL` - Model identifier (e.g., "openai/gpt-4o")
- `LLM_API_KEY` - API key for LLM service
- `LLM_MAX_TOKENS` - Maximum tokens in response
- `LLM_TEMPERATURE` - Sampling temperature (0.0 - 2.0)

#### ExtractorSettings

Document extraction configuration.

```python
class ExtractorSettings(BaseSettings):
    extractor_tmp_folder: str
    extractor_max_file_size_mb: int
    extractor_max_retries: int
```

**Methods:**

- `validate_tmp_folder()` - Validates temp folder exists or creates it

**Environment Variables:**

- `EXTRACTOR_TMP_FOLDER` - Temporary folder for extraction
- `EXTRACTOR_MAX_FILE_SIZE_MB` - Maximum file size in MB
- `EXTRACTOR_MAX_RETRIES` - Max retry attempts for extraction

#### TemporalSettings

Temporal.io workflow engine configuration.

```python
class TemporalSettings(BaseSettings):
    temporal_host: str
    temporal_namespace: str
    temporal_task_queue: str
```

**Environment Variables:**

- `TEMPORAL_HOST` - Temporal server host:port
- `TEMPORAL_NAMESPACE` - Temporal namespace
- `TEMPORAL_TASK_QUEUE` - Default task queue name

#### LogSettings

Logging configuration.

```python
class LogSettings(BaseSettings):
    gdai_log_level: str
    gdai_log_format: str
```

**Environment Variables:**

- `GDAI_LOG_LEVEL` - Log level (DEBUG, INFO, WARNING, ERROR)
- `GDAI_LOG_FORMAT` - Log message format string

#### Settings (Main)

Main settings class that aggregates all settings.

```python
class Settings(BaseSettings):
    database: DatabaseSettings
    s3: S3Settings
    embedding: EmbeddingSettings
    llm: LLMSettings
    extractor: ExtractorSettings
    temporal: TemporalSettings
    log: LogSettings
```

**Functions:**

- `get_settings()` - Returns cached singleton Settings instance (uses `@lru_cache`)

**Usage:**

```python
from gdai.commons.settings import get_settings

settings = get_settings()
db_url = settings.database.get_url()
```

---

### enums.py - Type Enums

Enumeration types used throughout the system.

#### DocumentStatusEnum

```python
class DocumentStatusEnum(str, Enum):
    PROCESSED = "processed"
    EXTRACTION_FAILED = "extraction_failed"
    EMBEDDING_FAILED = "embedding_failed"
```

Represents document processing status.

#### DocumentTypeEnum

```python
class DocumentTypeEnum(str, Enum):
    PDF = "pdf"
```

Represents supported document types (currently only PDF).

#### ChunkTypeEnum

```python
class ChunkTypeEnum(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"
```

Represents types of extracted chunks.

#### QueryStatusEnum

```python
class QueryStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
```

Represents query processing status.

---

### exceptions.py - Custom Exceptions

Structured exception hierarchy for error handling.

#### Base Exception

**GDAIException**

- `__init__(message, code, details)` - Base exception with structured error info
- `to_dict()` - Converts exception to dictionary format

#### Document Errors

**DocumentError** - Base exception for document-related errors

- `DocumentNotFoundError` - Document doesn't exist
- `DocumentAlreadyExistsError` - Document already exists
- `DocumentProcessingError` - Error during document processing

#### Extraction Errors

**ExtractionError** - Base exception for extraction errors

- `UnsupportedDocumentTypeError` - Document type not supported
- `ExtractionFailedError` - Extraction process failed

#### Chunk Errors

**ChunkError** - Base exception for chunk-related errors

- `ChunkNotFoundError` - Chunk doesn't exist

#### Query Errors

**QueryError** - Base exception for query-related errors

- `QueryNotFoundError` - Query doesn't exist
- `QueryProcessingError` - Error during query processing

#### Embedding Errors

**EmbeddingError** - Base exception for embedding errors

- `EmbeddingGenerationError` - Error generating embeddings

#### LLM Errors

**LLMError** - Base exception for LLM errors

- `LLMGenerationError` - Error during LLM generation

#### Storage Errors

**StorageError** - Base exception for storage errors

- `FileNotFoundError` - File doesn't exist in storage
- `FileUploadError` - Error uploading file

#### Validation Errors

**ValidationError** - Base exception for validation errors

- `InvalidInputError` - Invalid input provided

#### Authentication Errors

**AuthenticationError** - Base exception for auth errors

- `UnauthorizedError` - Authentication failed
- `ForbiddenError` - Permission denied

#### Workflow Errors

**WorkflowError** - Base exception for Temporal workflow errors

- `WorkflowExecutionError` - Workflow execution failed
- `WorkflowNotFoundError` - Workflow doesn't exist

**Usage:**

```python
from gdai.commons.exceptions import DocumentNotFoundError

raise DocumentNotFoundError(
    message="Document not found",
    code="DOC_NOT_FOUND",
    details={"document_id": doc_id}
)
```

---

### logger.py - Logging System

Singleton logger with color formatting and module path tracking.

#### ColorFormatter

Custom log formatter with ANSI color codes.

**Methods:**

- `format(record)` - Formats log record with colors based on level

**Colors:**

- DEBUG: Cyan
- INFO: Green
- WARNING: Yellow
- ERROR: Red
- CRITICAL: Bold Red

#### ModulePathFilter

Filter that adds module path information to log records.

**Methods:**

- `filter(record)` - Enriches log record with module path

#### Logger

Singleton logger instance.

**Methods:**

- `__new__()` - Creates singleton instance
- `__init__()` - Initializes logger (only once)
- `info(message)` - Logs info message
- `warning(message)` - Logs warning message
- `error(message)` - Logs error message
- `debug(message)` - Logs debug message
- `critical(message)` - Logs critical message
- `exception(message)` - Logs exception with traceback

**Usage:**

```python
from gdai.commons.logger import Logger

logger = Logger()
logger.info("Document processed successfully")
logger.error("Failed to extract document", exc_info=True)
```

**Configuration:**
Logger behavior is controlled by `LogSettings` from environment variables.

---

## Dependencies

- `pydantic-settings` - Settings management
- `python-dotenv` - .env file loading
- Standard library: `enum`, `logging`, `pathlib`

## Related Specifications

- [Overview](./overview.md) - Project overview
- [Repositories](./repositories.md) - Uses settings for database config
- [Services](./services.md) - Uses settings for external services
- All workflows use commons for configuration and error handling
