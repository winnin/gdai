# GDAI - Project Overview

## What is GDAI?

**GDAI** (Generative Document AI) is a multi-tenant vector store platform with auditable semantic search capabilities. It provides a robust infrastructure for document processing, embedding generation, and semantic search using Retrieval-Augmented Generation (RAG) techniques.

## Key Technologies

| Category            | Technology            | Purpose                                 |
| ------------------- | --------------------- | --------------------------------------- |
| **Language**        | Python 3.12+          | Modern Python with type hints           |
| **Package Manager** | UV                    | Fast dependency management              |
| **Orchestration**   | Temporal.io           | Workflow engine for document processing |
| **Database**        | PostgreSQL + pgvector | Vector storage with SQL                 |
| **Object Storage**  | MinIO / AWS S3        | Document storage                        |
| **Embeddings**      | Cohere embed-v4.0     | Text embeddings (1536 dimensions)       |
| **LLM**             | OpenAI GPT-4o         | Answer generation                       |
| **Web Framework**   | FastAPI               | REST API                                |
| **ORM**             | SQLAlchemy 2.0+       | Async database operations               |
| **Text Processing** | PyMuPDF, Chonkie      | PDF extraction and chunking             |

## Main Capabilities

- **Multi-tenant document storage** with complete data isolation per tenant
- **PDF document extraction** with text, table, and image extraction
- **Semantic chunking** with configurable strategies (sentence-based, etc.)
- **Vector embeddings generation** with Cohere's embed-v4.0 model
- **Semantic search** using cosine similarity with configurable thresholds
- **RAG-based Q&A** with source attribution and auditability
- **S3-compatible storage** with tenant isolation
- **Temporal workflows** for reliable, retryable document processing

## System Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│         FastAPI REST API            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Temporal.io Workflows          │
│  ┌───────────────────────────────┐  │
│  │ Upload File Workflow          │  │
│  │ Extract Document Workflow     │  │
│  │ Embed Texts Workflow          │  │
│  │ Search Documents Workflow     │  │
│  │ Conversational LLM Workflow   │  │
│  │ Document Management Workflow  │  │
│  └───────────────────────────────┘  │
└──────────────┬──────────────────────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │   MinIO/S3  │
│ + pgvector  │ │   Storage   │
└─────────────┘ └─────────────┘
```

## Document Processing Flow

```
1. Document Upload → S3/MinIO
   └─ Workflow: UploadFileWorkflow

2. Trigger Document Extraction
   └─ Workflow: DocumentExtractionWorkflow
      ├─ Download from S3
      ├─ Extract text/metadata (PDF, etc)
      ├─ Save to database
      └─ Trigger Embedding Workflow

3. Generate Embeddings
   └─ Workflow: TextEmbeddingWorkflow
      ├─ Chunk text into semantic units
      ├─ Generate embeddings (Cohere)
      └─ Store vectors in pgvector

4. Semantic Search
   └─ Workflow: DocumentSearchWorkflow
      ├─ Generate query embedding
      ├─ Vector similarity search
      └─ Return ranked results

5. RAG-based Q&A
   └─ Workflow: LLMWorkflow
      ├─ Search relevant chunks
      ├─ Build context
      ├─ Generate answer (OpenAI)
      └─ Return answer + sources
```

## Project Structure

```
gdai/
├── commons/              # Shared utilities, settings, enums, exceptions
├── repositories/         # Data access layer (PostgreSQL + pgvector)
├── services/            # Business logic (extractors, chunkers, embeddings, LLMs)
├── temporal/            # Temporal.io workflows and activities
│   ├── upload_file/
│   ├── extract_document/
│   ├── embedding_texts/
│   ├── document_management/
│   ├── search_on_documents/
│   └── conversational_llm/
└── scripts/             # Utility scripts (setup_db, reset_db, etc.)

tests/
├── unit/                # 155 unit tests (no external dependencies)
├── integration/         # 103 integration tests (+ 36 API-dependent)
└── e2e/                # End-to-end workflow tests
```

## Test Coverage

- **Total Tests**: 258 (155 unit + 103 integration)
- **Coverage**: 77%
- **Unit Tests**: Pure logic tests, no external dependencies
- **Integration Tests**: Require PostgreSQL, MinIO, and optionally API keys
- **CI/CD**: Automated testing via GitHub Actions

## Multi-Tenant Isolation

Every entity in GDAI is isolated by `tenant_id`:

- **Documents**: Each document belongs to a tenant
- **Chunks**: Each chunk inherits tenant_id from parent document
- **Queries**: Each query is tenant-specific
- **S3 Storage**: Files are stored with tenant prefix (`{tenant_id}/{filename}`)
- **Database Queries**: All queries filter by tenant_id

## Key Features

### Auditability

- Every query is stored with its answer and source chunks
- Full traceability from answer back to original document pages
- Query history preserved per tenant

### Scalability

- Temporal workflows allow horizontal scaling
- PostgreSQL connection pooling
- Batch processing for embeddings
- S3 storage for large files

### Reliability

- Temporal workflows handle retries automatically
- Transaction management for database operations
- Error handling with custom exceptions
- Health checks for all services

## Environment Configuration

All configuration is managed through Pydantic Settings:

- **Database Settings**: Connection pool, timeouts
- **S3 Settings**: Endpoint, credentials, bucket
- **Embedding Settings**: Model, dimensions, batch size
- **LLM Settings**: Model, temperature, max tokens
- **Temporal Settings**: Host, namespace, task queues
- **Extractor Settings**: Temp folder, max file size

See [.env.example](../../.env.example) for full configuration options.

## Related Specifications

- [Commons](./commons.md) - Shared utilities, settings, enums
- [Repositories](./repositories.md) - Data access layer
- [Services](./services.md) - Business logic layer
- [Upload File Workflow](./upload-file-workflow.md)
- [Extract Document Workflow](./extract-document-workflow.md)
- [Embedding Texts Workflow](./embedding-texts-workflow.md)
- [Document Management Workflow](./document-management-workflow.md)
- [Search Documents Workflow](./search-documents-workflow.md)
- [Conversational LLM Workflow](./conversational-llm-workflow.md)
- [Testing](./testing.md) - Test structure and strategies
