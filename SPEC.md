# GDAI Technical Specification

## 1. Project Overview

**GDAI** (Generative Document AI) is a multi-tenant vector store platform with auditable semantic search capabilities. It provides a robust infrastructure for document processing, embedding generation, and semantic search using Retrieval-Augmented Generation (RAG) techniques. The system is built on Temporal.io workflows for reliable, scalable processing pipelines with full observability.

**Key Technologies:**

- Python 3.12+
- Temporal.io (workflow orchestration)
- PostgreSQL + pgvector (vector similarity search)
- MinIO/AWS S3 (object storage)
- Cohere embed-v4.0 (text embeddings, 1536 dimensions)
- OpenAI GPT-4o (language model)
- FastAPI (web framework)
- SQLAlchemy 2.0+ (async ORM)
- LangChain (LLM orchestration)
- PyMuPDF (PDF extraction)
- Chonkie (text chunking)

**Main Capabilities:**

- Multi-tenant document storage and processing with complete data isolation
- PDF document extraction and semantic chunking
- Vector embeddings generation and storage with pgvector
- Semantic search with cosine similarity and configurable thresholds
- RAG-based question answering with source attribution
- S3-compatible object storage for documents (tenant-isolated)
- Temporal workflows for reliable, retryable document processing

**Test Coverage:**

- 155 unit tests (100% passing) - Pure tests with no external dependencies
- 103 integration tests (100% passing) - Tests requiring PostgreSQL, MinIO, Cohere, OpenAI
- Flat test structure for easy navigation (no nested subdirectories)
- Clear separation between unit and integration tests

---

## 2. Source Code Structure (gdai/)

### gdai/commons/

Configuration, logging, enums, exceptions, and settings for the application.

#### config.py

- `ConfigComponent` - Base configuration component with validation
- `ConfigComponent.validate()` - Validates configuration (returns bool)
- `DatabaseConfig` - Database connection configuration
- `DatabaseConfig.validate()` - Validates database settings
- `LLMConfig` - AI models configuration
- `LLMConfig.validate()` - Validates LLM settings
- `ExtractorConfig` - Document extractor configuration
- `ExtractorConfig.validate()` - Validates extractor settings
- `EmbeddingConfig` - Document embedding service configuration
- `EmbeddingConfig.validate()` - Validates embedding settings
- `Config` - Main configuration class grouping all components
- `Config.validate_all()` - Validates all configuration components
- `Config.get_component()` - Gets configuration component by name

#### enums.py

- `DocumentStatusEnum` - Document processing status (processed, extraction_failed, embedding_failed)
- `DocumentTypeEnum` - Document type (pdf)
- `ChunkTypeEnum` - Chunk type (text, image, table)
- `QueryStatusEnum` - Query status (pending, completed, failed)

#### exceptions.py

- `GDAIException.__init__()` - Initializes base exception with message, code, details
- `GDAIException.to_dict()` - Converts exception to dictionary format
- `DocumentError` - Base exception for document errors
- `DocumentNotFoundError.__init__()` - Exception when document not found
- `DocumentAlreadyExistsError.__init__()` - Exception when document exists
- `DocumentProcessingError.__init__()` - Exception when processing fails
- `ExtractionError` - Base exception for extraction errors
- `UnsupportedDocumentTypeError.__init__()` - Exception for unsupported types
- `ExtractionFailedError.__init__()` - Exception when extraction fails
- `ChunkError` - Base exception for chunk errors
- `ChunkNotFoundError.__init__()` - Exception when chunk not found
- `QueryError` - Base exception for query errors
- `QueryNotFoundError.__init__()` - Exception when query not found
- `QueryProcessingError.__init__()` - Exception when query processing fails
- `EmbeddingError` - Base exception for embedding errors
- `EmbeddingGenerationError.__init__()` - Exception when embedding generation fails
- `LLMError` - Base exception for LLM errors
- `LLMGenerationError.__init__()` - Exception when LLM generation fails
- `StorageError` - Base exception for storage errors
- `FileNotFoundError.__init__()` - Exception when file not found
- `FileUploadError.__init__()` - Exception when file upload fails
- `ValidationError` - Base exception for validation errors
- `InvalidInputError.__init__()` - Exception for invalid input
- `AuthenticationError` - Base exception for authentication errors
- `UnauthorizedError.__init__()` - Exception when authentication fails
- `ForbiddenError.__init__()` - Exception when permission denied
- `WorkflowError` - Base exception for workflow errors
- `WorkflowExecutionError.__init__()` - Exception when workflow execution fails
- `WorkflowNotFoundError.__init__()` - Exception when workflow not found

#### logger.py

- `ColorFormatter` - Logging formatter with color support
- `ColorFormatter.format()` - Formats log record with colors
- `ModulePathFilter` - Filter adding module path information
- `ModulePathFilter.filter()` - Filters and enriches log records
- `Logger.__new__()` - Singleton logger instance creation
- `Logger.__init__()` - Initializes logger instance once
- `Logger.info()` - Logs info message
- `Logger.warning()` - Logs warning message
- `Logger.error()` - Logs error message
- `Logger.debug()` - Logs debug message
- `Logger.critical()` - Logs critical message
- `Logger.exception()` - Logs exception with traceback

#### settings.py

- `DatabaseSettings` - Database configuration from environment
- `DatabaseSettings.validate_pool_size()` - Validates pool size configuration
- `DatabaseSettings.get_url()` - Gets PostgreSQL connection URL
- `EmbeddingSettings` - Embedding model configuration
- `EmbeddingSettings.validate_dimension()` - Validates embedding dimension
- `LLMSettings` - LLM configuration
- `LLMSettings.validate_temperature()` - Validates temperature range
- `ExtractorSettings` - Extractor configuration
- `ExtractorSettings.validate_tmp_folder()` - Validates temp folder exists
- `TemporalSettings` - Temporal configuration
- `S3Settings` - S3/MinIO storage configuration
- `Settings.__init__()` - Initializes all settings from environment
- `get_settings()` - Gets cached settings instance

### gdai/repositories/

Database models and repository pattern for data access.

#### base_repository.py

- `BaseRepository.__init__()` - Initializes base repository
- `BaseRepository.get_all_documents()` - Retrieves all documents for tenant
- `BaseRepository.get_document()` - Retrieves document by ID
- `BaseRepository.insert_document()` - Inserts new document
- `BaseRepository.delete_document()` - Deletes document by ID
- `BaseRepository.insert_chunks()` - Inserts multiple chunks
- `BaseRepository.get_chunks()` - Retrieves chunks for document
- `BaseRepository.get_chunks_without_embedding()` - Gets chunks without embeddings
- `BaseRepository.delete_chunks()` - Deletes chunks for document
- `BaseRepository.update_chunks()` - Updates multiple chunks
- `BaseRepository.insert_query()` - Inserts new query
- `BaseRepository.search_chunks_by_similarity_on_document_ids()` - Vector similarity search
- `BaseRepository.get_query()` - Retrieves query by ID

#### database.py

- `DatabaseManager.get_engine()` - Gets or creates database engine
- `DatabaseManager._create_engine()` - Creates new async engine
- `DatabaseManager.get_session_factory()` - Gets or creates session factory
- `DatabaseManager.create_session()` - Creates new database session
- `DatabaseManager.dispose()` - Disposes engine and clears cache
- `DatabaseManager.health_check()` - Checks database connection health

#### models.py

- `BaseModelMixin` - Base model with id, tenant_id, timestamps
- `DocumentModel` - Document table model with name, status, type, s3_path
- `ChunkModel` - Chunk table model with type, chunk, page_number, embedding
- `QueryModel` - Query table model with query, result, similarity, status
- `QueryChunkLinkModel` - Query-chunk link with similarity_score

#### pgvector_repository.py

- `PGVectorRepository.__init__()` - Initializes repository with optional session
- `PGVectorRepository.__aenter__()` - Enters async context manager
- `PGVectorRepository.__aexit__()` - Exits async context manager
- `PGVectorRepository._get_session()` - Gets current session
- `PGVectorRepository.get_all_documents()` - Lists all documents for tenant
- `PGVectorRepository.get_document()` - Gets document by ID
- `PGVectorRepository.insert_document()` - Inserts document to database
- `PGVectorRepository.delete_document()` - Deletes document and chunks
- `PGVectorRepository.insert_chunks()` - Inserts chunks in batches
- `PGVectorRepository.insert_batch_chunks()` - Bulk insert chunks
- `PGVectorRepository.get_chunks()` - Gets all chunks for document
- `PGVectorRepository.get_chunks_without_embedding()` - Gets chunks needing embeddings
- `PGVectorRepository.delete_chunks()` - Deletes all chunks for document
- `PGVectorRepository.update_chunks()` - Updates chunks in database
- `PGVectorRepository.insert_query()` - Inserts query to database
- `PGVectorRepository.update_query_result()` - Updates query result and status
- `PGVectorRepository.get_query()` - Gets query by ID
- `PGVectorRepository.get_all_queries()` - Gets all queries for tenant
- `PGVectorRepository.search_chunks_by_similarity_on_document_ids()` - Cosine similarity search
- `PGVectorRepository.insert_query_chunk_links()` - Links query to chunks

#### sqlalchemy.py

- `Base` - SQLAlchemy declarative base for models

### gdai/services/

Service layer for document processing, embeddings, LLMs, and storage.

#### chunkers.py

- `BaseChunker.__init__()` - Initializes chunker with strategy
- `BaseChunker.chunk()` - Chunks input text (abstract method)
- `BaseChunker.__str__()` - Returns strategy name
- `DocumentTextChunkerBySentence.__init__()` - Initializes sentence chunker
- `DocumentTextChunkerBySentence._clean_text()` - Cleans text removing line breaks
- `DocumentTextChunkerBySentence.chunk()` - Chunks texts by sentences
- `ChunkerFactory.get_chunker()` - Creates chunker by type

#### embeddings.py

- `EmbeddingModel.__init__()` - Initializes embedding model
- `EmbeddingModel.generate_texts_embeddings()` - Generates embeddings (abstract)
- `EmbeddingModel.__str__()` - Returns model name
- `CohereEmbeddingModel.__init__()` - Initializes Cohere model
- `CohereEmbeddingModel.create()` - Creates Cohere model with API key
- `CohereEmbeddingModel.normalize_embedding()` - Normalizes vector to unit length
- `CohereEmbeddingModel.generate_texts_embeddings()` - Generates Cohere embeddings
- `EmbeddingFactory.get_embedding()` - Creates embedding model from settings

#### extractors.py

- `DocumentExtractor.__init__()` - Initializes document extractor
- `DocumentExtractor.extract_document_data()` - Extracts text from document (abstract)
- `PDFExtractor.__init__()` - Initializes PDF extractor
- `PDFExtractor.extract_document_data()` - Extracts PDF text, tables, images
- `PDFExtractor._extract_raw_text()` - Extracts raw text from PDF pages
- `PDFExtractor._extract_raw_tables()` - Extracts tables from PDF
- `PDFExtractor._extract_raw_images()` - Extracts images from PDF
- `ExtractorFactory.get_extractor()` - Creates extractor by type

#### llms.py

- `LLMModel.__init__()` - Initializes LLM model
- `LLMModel.call_llm()` - Generates text from prompt (abstract)
- `LLMModel.__str__()` - Returns model name
- `OpenAIModel.__init__()` - Initializes OpenAI model
- `OpenAIModel.create()` - Creates OpenAI model with API key
- `OpenAIModel.call_llm()` - Calls OpenAI API with prompt
- `LLMFactory.get_llm()` - Creates LLM model from settings

#### s3_storage.py

- `S3StorageService.__init__()` - Initializes S3 service with settings
- `S3StorageService._ensure_bucket_exists()` - Creates bucket if missing
- `S3StorageService.get_s3_key()` - Generates S3 key with tenant prefix
- `S3StorageService.upload_file()` - Uploads file to S3 with tenant isolation
- `S3StorageService.upload_fileobj()` - Uploads file object to S3
- `S3StorageService.download_file()` - Downloads file from S3
- `S3StorageService.delete_file()` - Deletes file from S3
- `S3StorageService.file_exists()` - Checks if file exists in S3
- `S3StorageService.get_file_url()` - Gets full S3 URL
- `S3StorageService.list_files()` - Lists files for tenant
- `get_s3_storage()` - Gets S3 storage service instance

### gdai/temporal/

Temporal.io workflows, activities, and workers for document processing.

#### client.py

- `TemporalClientManager.get_client()` - Gets or creates Temporal client
- `TemporalClientManager._create_client()` - Creates new Temporal client
- `TemporalClientManager.close()` - Closes Temporal client connection
- `TemporalClientManager.health_check()` - Checks Temporal connection health

#### main.py

- `main()` - Runs all Temporal workers concurrently

#### conversational_llm/

##### activity.py

- `chat_llm()` - Activity calling LLM for text generation

##### schema.py

- `ChatInput` - Input schema with user_prompt, system_prompt

##### workflow.py

- `LLMWorkflow.run()` - Workflow executing LLM chat activity

##### worker.py

- `main()` - Starts LLM worker on llm-queue

#### document_management/

##### activity.py

- `list_documents()` - Activity listing documents for tenant
- `get_document()` - Activity getting document by ID
- `delete_document()` - Activity deleting document and chunks
- `get_document_chunks()` - Activity getting chunks for document
- `get_document_status()` - Activity getting document status

##### schema.py

- `ListDocumentsInput` - Input with tenant_id
- `ListDocumentsOutput` - Output with documents list and total
- `GetDocumentInput` - Input with tenant_id, document_id
- `Document` - Document schema with metadata
- `DeleteDocumentInput` - Input with tenant_id, document_id
- `GetDocumentChunksInput` - Input with tenant_id, document_id
- `GetDocumentChunksOutput` - Output with chunks list and total
- `Chunk` - Chunk schema with content and metadata
- `GetDocumentStatusInput` - Input with tenant_id, document_id
- `DocumentStatus` - Status schema with processing info

##### workflow.py

- `ListDocumentsWorkflow.run()` - Workflow listing all documents
- `GetDocumentWorkflow.run()` - Workflow getting document details
- `DeleteDocumentWorkflow.run()` - Workflow deleting document
- `GetDocumentChunksWorkflow.run()` - Workflow getting document chunks
- `GetDocumentStatusWorkflow.run()` - Workflow getting document status

##### worker.py

- `main()` - Starts document management worker

#### embedding_texts/

##### activity.py

- `embedding_texts()` - Activity generating embeddings for texts

##### workflow.py

- `TextEmbeddingWorkflow.run()` - Workflow generating text embeddings

##### worker.py

- `main()` - Starts embedding worker on embedding-text-queue

#### extract_document/

##### activity.py

- `validate()` - Activity validating document in S3
- `save_document_metadata()` - Activity saving document to database
- `extract_document_content()` - Activity extracting PDF content
- `chunk_texts_to_batched_files()` - Activity chunking texts to files
- `get_chunk_file_content_for_embedding()` - Activity loading chunks from file
- `store_embedded_chunks()` - Activity storing chunks with embeddings
- `remove_temp_files()` - Activity cleaning up temporary files

##### schema.py

- `DocumentExtracInput` - Input with s3_key, chunk_strategy, tenant_id
- `ChunkDocumentInput` - Input with document_id, tenant_id, chunk_strategy
- `Document` - Document schema with chunks
- `Chunk` - Chunk schema with id, tenant_id, document_id, content

##### workflow.py

- `DocumentExtractionWorkflow._validate_document()` - Validates document input
- `DocumentExtractionWorkflow._save_document_metadata()` - Saves metadata
- `DocumentExtractionWorkflow._extract_document_content()` - Extracts content
- `DocumentExtractionWorkflow._chunk_texts_to_batched_files()` - Chunks texts
- `DocumentExtractionWorkflow._get_chunk_file_content_for_embedding()` - Embeds chunks
- `DocumentExtractionWorkflow._store_embedded_chunks()` - Stores chunks
- `DocumentExtractionWorkflow._cleanup_temp_files()` - Cleans temp files
- `DocumentExtractionWorkflow.run()` - Main extraction workflow

##### worker.py

- `main()` - Starts extraction worker on process-document-queue

#### search_on_documents/

##### activity.py

- `register_query()` - Activity registering query in database
- `get_chunks()` - Activity performing vector similarity search
- `generate_prompt_from_template()` - Activity generating LLM prompt
- `save_query_result()` - Activity saving query result
- `format_answer()` - Activity formatting final answer with sources

##### schema.py

- `SearchInput` - Input with query_id, tenant_id, query, params
- `QueryInput` - Input with query_id, tenant_id, query
- `ChunkSearchParam` - Search params with embedding, threshold, limit
- `PromptInput` - Input with query and chunks
- `UpdateQueryResultInput` - Input with query_id, answer, chunks
- `FormatAnswerInput` - Input with all search parameters
- `SearchResult` - Result with answer, chunks, metadata
- `ChunkInfo` - Chunk info with document_id, page, similarity

##### workflow.py

- `DocumentSearchWorkflow.run()` - Main search workflow with RAG

##### worker.py

- `main()` - Starts search worker on search-on-documents-queue

### gdai/scripts/

Shell scripts and Python utilities for development and database management.

#### dev.sh

- Shell script starting development environment

#### reset_db.py

- Python script dropping and recreating database tables

#### setup_db.py

- Python script creating database tables and indexes

#### tests.sh

- Shell script running test suite

---

## 3. Test Structure (tests/)

### tests/conftest.py

Pytest configuration and fixtures for all tests.

- `test_settings()` - Fixture providing test settings
- `event_loop()` - Fixture providing async event loop
- `db_engine()` - Fixture creating test database engine
- `db_session()` - Fixture providing test database session
- `sample_tenant_id()` - Fixture providing test tenant ID
- `cleanup_database()` - Fixture cleaning database after tests

### tests/unit/

Unit tests for individual components in isolation. All test files are located directly in tests/unit/ with no subdirectories, following a flat structure for easy navigation.

**Total: 155 tests (100% passing)**

#### test_chunkers.py

##### TestBaseChunker

- `test_base_chunker_initialization()` - Tests BaseChunker can be initialized
- `test_base_chunker_str_representation()` - Tests **str** returns strategy
- `test_base_chunker_chunk_is_abstract()` - Tests chunk method is abstract
- `test_base_chunker_chunk_method_returns_none()` - Tests base implementation

##### TestDocumentTextChunkerBySentence

- `test_sentence_chunker_initialization()` - Tests sentence chunker initialization
- `test_sentence_chunker_initialization_with_custom_min_sentences()` - Tests custom settings
- `test_sentence_chunker_inherits_from_base_chunker()` - Tests inheritance
- `test_sentence_chunker_str_representation()` - Tests **str** method
- `test_clean_text_removes_line_breaks()` - Tests line break removal
- `test_clean_text_fixes_unicode()` - Tests unicode error handling
- `test_clean_text_preserves_content()` - Tests content preservation
- `test_clean_text_handles_empty_string()` - Tests empty string handling
- `test_clean_text_handles_whitespace_only()` - Tests whitespace handling
- `test_chunk_single_page()` - Tests chunking single page
- `test_chunk_multiple_pages()` - Tests chunking multiple pages
- `test_chunk_empty_list()` - Tests empty input handling
- `test_chunk_empty_strings()` - Tests empty strings handling
- `test_chunk_returns_cleaned_text()` - Tests text cleaning in output
- `test_chunk_preserves_text_content()` - Tests content preservation
- `test_chunk_with_long_text()` - Tests long text chunking
- `test_chunk_with_short_text()` - Tests short text handling
- `test_chunk_with_special_characters()` - Tests special character handling
- `test_chunk_with_unicode_characters()` - Tests unicode handling

##### TestChunkerFactory

- `test_factory_get_sentence_chunker()` - Tests factory returns sentence chunker
- `test_factory_returns_new_instance_each_time()` - Tests new instances
- `test_factory_unknown_chunker_type_raises_error()` - Tests error for unknown type
- `test_factory_invalid_type_raises_error()` - Tests various invalid types
- `test_factory_is_static_method()` - Tests static method behavior
- `test_factory_does_not_require_instantiation()` - Tests factory usage

##### TestChunkersIntegration

- `test_sentence_chunker_end_to_end()` - Tests complete chunking workflow
- `test_chunker_strategy_attribute()` - Tests strategy attribute
- `test_multiple_chunkers_independent()` - Tests chunker independence

#### test_config.py

Tests for configuration validation and loading (50 tests covering DatabaseConfig, LLMConfig, ExtractorConfig, EmbeddingConfig).

#### test_enums.py

Tests for enum types and values (11 tests for DocumentStatusEnum, DocumentTypeEnum, ChunkTypeEnum, QueryStatusEnum).

#### test_extractors.py

Tests for PDF and document extractors (31 tests including real PDF extraction tests).

#### test_logger.py

Tests for logging configuration and formatting (27 tests for Logger, formatters, filters, handlers).

### tests/integration/

Integration tests for components working together with external services. All test files are located directly in tests/integration/ with no subdirectories.

**Total: 103 tests passing, 36 skipped (API-dependent tests)**

#### test_document_flow.py

Tests for end-to-end document processing flow (3 tests: upload/store, deletion, multi-tenant isolation).

#### test_document_management_activities.py

Tests for document management Temporal activities (7 tests: list, get, delete documents with S3 integration).

#### test_embeddings.py

Tests for embedding generation with Cohere API (24 tests - skipped without API key).

#### test_extract_activities.py

Tests for document extraction Temporal activities (15 tests: validation, metadata saving, content extraction).

#### test_llms.py

Tests for LLM integration with OpenAI (27 tests - skipped without API key).

#### test_pgvector_repository.py

Tests for PGVectorRepository direct usage (15 tests: document CRUD, chunks, tenant isolation, context manager).

#### test_repositories.py

Tests for repository pattern implementations (22 tests: documents, chunks, vector search, queries, RAG workflow).

#### test_s3_storage.py

Tests for S3/MinIO storage operations (21 tests: upload, download, delete, list, tenant isolation).

### tests/e2e/

End-to-end tests for complete workflows with all services.

#### test_chunk_embedding.py

Tests for chunking and embedding complete workflow.

#### test_embedding.py

Tests for embedding generation workflow.

#### test_extraction.py

Tests for document extraction workflow end-to-end.

#### test_llm.py

Tests for LLM conversation workflow.

#### test_search.py

Tests for semantic search workflow with RAG.

### tests/mocks/

Mock implementations for external APIs.

#### external_apis.py

Mock classes for Cohere and OpenAI APIs used in tests.

---

**End of Specification**
