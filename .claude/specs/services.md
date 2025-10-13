# Services - Business Logic Layer

This module contains business logic for document processing, including extraction, chunking, embedding generation, LLM interactions, and S3 storage.

## Location

`gdai/services/`

## Components

### extractors.py - Document Extraction

Extracts text, tables, and images from documents.

#### DocumentExtractor (Abstract Base)

Base class for document extractors.

**Methods:**

- `__init__(strategy: str)` - Initializes with strategy name
- `extract_document_data(file_path: str) -> Dict` - Abstract method for extraction

#### PDFExtractor

Extracts content from PDF documents using PyMuPDF.

**Initialization:**

```python
extractor = PDFExtractor()
```

**Methods:**

- `extract_document_data(file_path: str) -> Dict`

  - Main extraction method
  - Returns: `{"texts": List[str], "tables": List[str], "images": List[bytes]}`
  - Raises: `ExtractionFailedError` on failure

- `_extract_raw_text(doc: fitz.Document) -> List[str]`

  - Extracts raw text from all PDF pages
  - Returns list of text strings (one per page)

- `_extract_raw_tables(doc: fitz.Document) -> List[str]`

  - Extracts tables from PDF
  - Returns list of table strings

- `_extract_raw_images(doc: fitz.Document) -> List[bytes]`
  - Extracts images from PDF
  - Returns list of image data as bytes

**Configuration:**

Uses `ExtractorSettings`:

- `extractor_tmp_folder` - Temporary folder for processing
- `extractor_max_file_size_mb` - Maximum file size
- `extractor_max_retries` - Retry attempts

**Usage:**

```python
from gdai.services.extractors import PDFExtractor

extractor = PDFExtractor()
data = extractor.extract_document_data("/path/to/file.pdf")
texts = data["texts"]  # List of page texts
```

#### ExtractorFactory

Factory for creating extractors based on document type.

**Methods:**

- `get_extractor(doc_type: DocumentTypeEnum) -> DocumentExtractor`
  - Returns appropriate extractor for document type
  - Currently supports: `DocumentTypeEnum.PDF` → `PDFExtractor`
  - Raises: `UnsupportedDocumentTypeError` for unknown types

**Usage:**

```python
from gdai.services.extractors import ExtractorFactory
from gdai.commons.enums import DocumentTypeEnum

extractor = ExtractorFactory.get_extractor(DocumentTypeEnum.PDF)
```

---

### chunkers.py - Text Chunking

Splits text into semantic chunks for embedding generation.

#### BaseChunker (Abstract Base)

Base class for text chunking strategies.

**Methods:**

- `__init__(strategy: str)` - Initializes with strategy name
- `chunk(texts: List[str]) -> List[Dict]` - Abstract chunking method
- `__str__()` - Returns strategy name

#### DocumentTextChunkerBySentence

Chunks text by sentences using Chonkie library.

**Initialization:**

```python
chunker = DocumentTextChunkerBySentence(
    chunk_size=512,        # tokens per chunk
    chunk_overlap=128,     # overlap between chunks
    min_sentences=1        # minimum sentences per chunk
)
```

**Methods:**

- `chunk(texts: List[str]) -> List[Dict]`

  - Chunks input texts by sentences
  - Returns: `List[{"page_number": int, "content": str, "type": ChunkTypeEnum}]`
  - Preserves page numbers from input

- `_clean_text(text: str) -> str`
  - Cleans text by removing line breaks
  - Fixes unicode encoding errors
  - Normalizes whitespace

**Features:**

- Semantic chunking (respects sentence boundaries)
- Configurable chunk size and overlap
- Automatic text cleaning
- Page number preservation

**Usage:**

```python
from gdai.services.chunkers import DocumentTextChunkerBySentence

chunker = DocumentTextChunkerBySentence(chunk_size=512, chunk_overlap=128)
chunks = chunker.chunk(["Page 1 text", "Page 2 text"])
# chunks = [
#   {"page_number": 1, "content": "...", "type": ChunkTypeEnum.TEXT},
#   {"page_number": 2, "content": "...", "type": ChunkTypeEnum.TEXT}
# ]
```

#### ChunkerFactory

Factory for creating chunkers.

**Methods:**

- `get_chunker(chunker_type: str, **kwargs) -> BaseChunker`
  - Returns chunker instance
  - Currently supports: `"sentence"` → `DocumentTextChunkerBySentence`
  - Raises: `ValueError` for unknown types

**Usage:**

```python
from gdai.services.chunkers import ChunkerFactory

chunker = ChunkerFactory.get_chunker("sentence", chunk_size=512)
```

---

### embeddings.py - Embedding Generation

Generates vector embeddings for text using external APIs.

#### EmbeddingModel (Abstract Base)

Base class for embedding models.

**Methods:**

- `__init__(model: str)` - Initializes with model name
- `generate_texts_embeddings(texts: List[str]) -> List[List[float]]` - Abstract embedding method
- `__str__()` - Returns model name

#### CohereEmbeddingModel

Generates embeddings using Cohere's embed-v4.0 model.

**Initialization:**

```python
model = CohereEmbeddingModel.create(
    model="cohere/embed-v4.0",
    api_key="your-api-key",
    dimension=1536,
    batch_size=96
)
```

**Methods:**

- `create(model: str, api_key: str, dimension: int, batch_size: int) -> CohereEmbeddingModel`

  - Factory method for creating model instance
  - Validates API key and settings

- `generate_texts_embeddings(texts: List[str]) -> List[List[float]]`

  - Generates embeddings for list of texts
  - Processes in batches for efficiency
  - Returns normalized embeddings (unit length)
  - Raises: `EmbeddingGenerationError` on failure

- `normalize_embedding(embedding: List[float]) -> List[float]`
  - Normalizes vector to unit length
  - Used for cosine similarity

**Features:**

- Batch processing for efficiency
- Automatic retry on API failures
- Vector normalization
- Error handling with custom exceptions

**Configuration:**

Uses `EmbeddingSettings`:

- `embedding_model` - Model identifier
- `embedding_api_key` - API key
- `embedding_dimension` - Vector dimension (1536)
- `embedding_batch_size` - Batch size (96)
- `embedding_max_retries` - Retry attempts

**Usage:**

```python
from gdai.services.embeddings import CohereEmbeddingModel
from gdai.commons.settings import get_settings

settings = get_settings()
model = CohereEmbeddingModel.create(
    model=settings.embedding.embedding_model,
    api_key=settings.embedding.embedding_api_key,
    dimension=settings.embedding.embedding_dimension,
    batch_size=settings.embedding.embedding_batch_size
)

texts = ["Hello world", "Another text"]
embeddings = model.generate_texts_embeddings(texts)
# embeddings = [[0.1, 0.2, ...], [0.3, 0.4, ...]]
```

#### EmbeddingFactory

Factory for creating embedding models.

**Methods:**

- `get_embedding() -> EmbeddingModel`
  - Creates embedding model from settings
  - Currently supports: Cohere
  - Raises: `ValueError` for unknown models

**Usage:**

```python
from gdai.services.embeddings import EmbeddingFactory

model = EmbeddingFactory.get_embedding()
embeddings = model.generate_texts_embeddings(texts)
```

---

### llms.py - Language Model Integration

Integrates with language models for text generation.

#### LLMModel (Abstract Base)

Base class for LLM implementations.

**Methods:**

- `__init__(model: str)` - Initializes with model name
- `call_llm(prompt: str, system_prompt: str) -> str` - Abstract generation method
- `__str__()` - Returns model name

#### OpenAIModel

Generates text using OpenAI's GPT models via LangChain.

**Initialization:**

```python
model = OpenAIModel.create(
    model="openai/gpt-4o",
    api_key="your-api-key",
    max_tokens=2000,
    temperature=0.7
)
```

**Methods:**

- `create(model: str, api_key: str, max_tokens: int, temperature: float) -> OpenAIModel`

  - Factory method for creating model instance
  - Validates API key and settings

- `call_llm(prompt: str, system_prompt: str = None) -> str`
  - Generates text from prompt
  - Optional system prompt for instructions
  - Returns generated text
  - Raises: `LLMGenerationError` on failure

**Features:**

- LangChain integration
- Configurable temperature and max tokens
- System prompt support
- Error handling with retries

**Configuration:**

Uses `LLMSettings`:

- `llm_model` - Model identifier (e.g., "openai/gpt-4o")
- `llm_api_key` - API key
- `llm_max_tokens` - Maximum response tokens
- `llm_temperature` - Sampling temperature (0.0 - 2.0)

**Usage:**

```python
from gdai.services.llms import OpenAIModel
from gdai.commons.settings import get_settings

settings = get_settings()
model = OpenAIModel.create(
    model=settings.llm.llm_model,
    api_key=settings.llm.llm_api_key,
    max_tokens=settings.llm.llm_max_tokens,
    temperature=settings.llm.llm_temperature
)

answer = model.call_llm(
    prompt="What is RAG?",
    system_prompt="You are a helpful AI assistant."
)
```

#### LLMFactory

Factory for creating LLM models.

**Methods:**

- `get_llm() -> LLMModel`
  - Creates LLM model from settings
  - Currently supports: OpenAI
  - Raises: `ValueError` for unknown models

**Usage:**

```python
from gdai.services.llms import LLMFactory

model = LLMFactory.get_llm()
answer = model.call_llm(prompt)
```

---

### s3_storage.py - Object Storage

Manages document storage in S3/MinIO with multi-tenant isolation.

#### S3StorageService

Service for S3/MinIO operations with tenant isolation.

**Initialization:**

```python
service = S3StorageService(settings)
```

**Methods:**

- `__init__(settings: Settings)`

  - Initializes S3 client with settings
  - Creates bucket if it doesn't exist

- `_ensure_bucket_exists() -> None`

  - Creates bucket if missing (internal method)

- `get_s3_key(tenant_id: str, filename: str) -> str`

  - Generates S3 key with tenant prefix
  - Format: `{tenant_id}/{filename}`
  - Ensures tenant isolation

- `upload_file(tenant_id: str, file_path: str, filename: str) -> str`

  - Uploads file from local path to S3
  - Returns S3 key
  - Raises: `FileUploadError` on failure

- `upload_fileobj(tenant_id: str, file_obj: BinaryIO, filename: str) -> str`

  - Uploads file object to S3
  - Returns S3 key
  - More efficient for in-memory files

- `download_file(s3_key: str, local_path: str) -> None`

  - Downloads file from S3 to local path
  - Raises: `FileNotFoundError` if not exists

- `delete_file(s3_key: str) -> None`

  - Deletes file from S3
  - Raises: `FileNotFoundError` if not exists

- `file_exists(s3_key: str) -> bool`

  - Checks if file exists in S3

- `get_file_url(s3_key: str) -> str`

  - Returns full S3 URL for file

- `list_files(tenant_id: str) -> List[str]`
  - Lists all files for tenant
  - Returns list of S3 keys

**Multi-Tenant Isolation:**

All files are stored with tenant prefix:

```
bucket/
  ├── tenant-1/
  │   ├── document1.pdf
  │   └── document2.pdf
  └── tenant-2/
      └── document3.pdf
```

**Configuration:**

Uses `S3Settings`:

- `s3_endpoint` - S3 endpoint URL
- `s3_access_key` - Access key
- `s3_secret_key` - Secret key
- `s3_bucket` - Bucket name
- `s3_region` - Region
- `s3_use_ssl` - Use SSL

**Usage:**

```python
from gdai.services.s3_storage import get_s3_storage

storage = get_s3_storage()

# Upload file
s3_key = storage.upload_file(
    tenant_id="tenant-1",
    file_path="/path/to/document.pdf",
    filename="document.pdf"
)

# Download file
storage.download_file(s3_key, "/tmp/document.pdf")

# List files
files = storage.list_files("tenant-1")
```

**Helper Function:**

- `get_s3_storage() -> S3StorageService`
  - Returns S3 storage service instance with settings from environment

---

## Service Layer Design

### Factory Pattern

All services use factory pattern for instantiation:

- `ExtractorFactory` - Creates document extractors
- `ChunkerFactory` - Creates text chunkers
- `EmbeddingFactory` - Creates embedding models
- `LLMFactory` - Creates LLM models

### Strategy Pattern

Services support different strategies:

- Extractors: PDF, (future: DOCX, TXT)
- Chunkers: Sentence-based, (future: token-based, semantic)
- Embeddings: Cohere, (future: OpenAI, local models)
- LLMs: OpenAI, (future: Anthropic, local models)

### Error Handling

All services use custom exceptions from `gdai.commons.exceptions`:

- `ExtractionFailedError` - Document extraction failures
- `EmbeddingGenerationError` - Embedding generation failures
- `LLMGenerationError` - LLM generation failures
- `FileUploadError` - S3 upload failures

---

## Dependencies

- `PyMuPDF` (fitz) - PDF extraction
- `Chonkie` - Semantic text chunking
- `LangChain` - LLM orchestration
- `boto3` - S3/MinIO client
- `cohere` - Cohere API client
- `openai` - OpenAI API client (via LangChain)

## Related Specifications

- [Overview](./overview.md) - Project overview
- [Commons](./commons.md) - Uses settings and exceptions
- [Repositories](./repositories.md) - Services persist data via repositories
- [Extract Document Workflow](./extract-document-workflow.md) - Uses extractors and chunkers
- [Embedding Texts Workflow](./embedding-texts-workflow.md) - Uses embedding service
- [Conversational LLM Workflow](./conversational-llm-workflow.md) - Uses LLM service
- [Upload File Workflow](./upload-file-workflow.md) - Uses S3 storage service
