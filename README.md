# GDAI: Multi-Tenant Vector Store with Auditable Semantic Search

GDAI is an open-source, production-ready platform for building intelligent document search systems. Built on **Temporal.io** for robust workflow orchestration, GDAI provides a complete pipeline from document ingestion to semantic search with full auditability and source traceability.

[![Tests](https://github.com/winnin/gdai/actions/workflows/tests.yml/badge.svg)](https://github.com/winnin/gdai/actions/workflows/tests.yml)
[![Pre-commit](https://github.com/winnin/gdai/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/winnin/gdai/actions/workflows/pre-commit.yml)
[![codecov](https://codecov.io/gh/winnin/gdai/branch/main/graph/badge.svg)](https://codecov.io/gh/winnin/gdai)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![Temporal](https://img.shields.io/badge/Temporal-Workflows-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST_API-green)

## Why GDAI?

Traditional RAG systems often lack reliability, observability, and auditability. GDAI solves these problems by:

- **Reliable Processing**: Built on Temporal.io workflows with automatic retries, state management, and fault tolerance
- **Multi-Tenant Architecture**: Isolate data and search spaces for multiple organizations with full tenant isolation
- **Complete Auditability**: Every answer is traceable to its source chunks, with similarity scores and provenance tracking
- **Production-Ready**: Async-first design, batch processing, connection pooling, and comprehensive error handling
- **Flexible & Extensible**: Plugin architecture for embeddings (Cohere, OpenAI), LLMs (OpenAI, custom), and document formats

## Architecture Overview

GDAI uses a **workflow-based architecture** powered by Temporal.io, ensuring reliable and observable document processing:

```
┌─────────────────┐
│   FastAPI API   │  ← REST endpoints for document upload & search
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              Temporal Workflows (Orchestration)              │
├──────────────┬──────────────┬──────────────┬────────────────┤
│   Document   │   Embedding  │     LLM      │     Search     │
│  Extraction  │   Workflow   │   Workflow   │    Workflow    │
│              │              │              │                │
│ • Validate   │ • Batch texts│ • Generate   │ • Embed query  │
│ • Extract    │ • Embed with │   prompts    │ • Vector search│
│ • Chunk      │   Cohere     │ • Call OpenAI│ • Format result│
│ • Store      │ • Normalize  │ • Return     │ • Save history │
└──────────────┴──────────────┴──────────────┴────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                PostgreSQL + pgvector                         │
│  • Documents metadata    • Chunks with embeddings            │
│  • Query history         • Query-Chunk relationships         │
└─────────────────────────────────────────────────────────────┘
```

## Key Features

### Document Processing Pipeline

- **Multi-format Support**: PDF extraction with PyMuPDF (tables and images planned)
- **Smart Chunking**: Sentence-based chunking with configurable strategies
- **Batch Processing**: Efficient batch embedding and storage operations
- **Fault Tolerance**: Automatic retries, timeout handling, and workflow recovery

### Semantic Search & RAG

- **Vector Similarity Search**: Cosine similarity with pgvector
- **RAG with Source Tracking**: Every answer includes source chunks with similarity scores
- **Flexible Filtering**: Search across all documents or filter by specific document IDs
- **Similarity Thresholds**: Configurable minimum similarity for results

### Multi-Tenancy

- **Tenant Isolation**: Complete data separation at database level
- **Per-Tenant Configuration**: Isolated document storage and search spaces
- **Scalable Design**: Handle multiple organizations with different data requirements

### Observability & Auditability

- **Workflow Visibility**: Monitor document processing in Temporal UI (http://localhost:8233)
- **Comprehensive Logging**: Structured logs with correlation IDs across workflows
- **Query History**: Track all queries, results, and source chunks
- **Performance Metrics**: Similarity scores and chunk tracking for each answer

## Getting Started

### Prerequisites

- **Python 3.12+** (3.11+ supported)
- **Docker & Docker Compose** (for PostgreSQL, Temporal, MinIO)
- **API Keys**:
  - Cohere API key (for embeddings)
  - OpenAI API key (for LLM)

### Quick Start

1. **Clone and install dependencies**:

   ```bash
   git clone https://github.com/winnin/gdai.git
   cd gdai

   # Install uv package manager (if not installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv sync
   ```

2. **Configure environment**:

   ```bash
   # Copy and edit environment variables
   cp .env.example .env

   # Edit .env and add your API keys:
   # EMBEDDING_MODEL_API_KEY=your-cohere-api-key
   # LLM_API_KEY=your-openai-api-key
   ```

3. **Start infrastructure services**:

   ```bash
   # Start PostgreSQL (with pgvector), Temporal, and MinIO
   docker-compose up -d

   # Initialize database
   task setup-db
   ```

4. **Start Temporal workers** (in a separate terminal):

   ```bash
   source .venv/bin/activate

   # Start all workers at once (recommended)
   task temporal-all

   # Or start workers individually:
   # task temporal-extract   # Document extraction worker
   # task temporal-embed     # Embedding worker
   # task temporal-llm       # LLM worker
   # task temporal-search    # Search worker
   ```

5. **Start the API server** (in another terminal):

   ```bash
   source .venv/bin/activate
   task run
   ```

6. **Access the services**:
   - **API Documentation**: http://localhost:8000/docs
   - **Temporal UI**: http://localhost:8233
   - **MinIO Console**: http://localhost:9001

### Usage Example

#### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/v1/document/upload" \
  -F "tenant_id=my-company" \
  -F "chunk_strategy=sentence" \
  -F "document_file=@/path/to/document.pdf"
```

Response:

```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "message": "Document uploaded and queued for processing",
  "document_name": "document.pdf",
  "tenant_id": "my-company",
  "status": "processing",
  "chunk_strategy": "sentence"
}
```

#### 2. Check Document Status

```bash
curl "http://localhost:8000/v1/document/my-company"
```

Response:

```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "document.pdf",
    "tenant_id": "my-company",
    "status": "processed",
    "chunk_strategy": "sentence",
    "number_of_chunks": 42,
    "created_at": "2025-10-10T12:00:00",
    "updated_at": "2025-10-10T12:02:30"
  }
]
```

#### 3. Search Documents

```bash
curl -X POST "http://localhost:8000/v1/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "my-company",
    "query_text": "What are the main findings?",
    "chunks_limit": 5,
    "similarity_threshold": 0.7
  }'
```

Response:

```json
{
  "query_id": "query-uuid",
  "tenant_id": "my-company",
  "query": "What are the main findings?",
  "answer": "Based on the documents, the main findings are...",
  "sources": [
    {
      "chunk_id": "chunk-uuid",
      "document_id": "doc-uuid",
      "document_name": "document.pdf",
      "page_number": 5,
      "chunk_text": "The main findings indicate...",
      "similarity_score": 0.89
    }
  ],
  "metadata": {
    "num_chunks_retrieved": 5,
    "chunk_strategy": "sentence",
    "similarity_threshold": 0.7
  }
}
```

## Temporal Workflows in Detail

GDAI leverages **Temporal.io** for orchestrating complex, long-running document processing workflows with built-in reliability, retries, and observability.

### Why Temporal?

- **Automatic Retries**: Failed activities are automatically retried with exponential backoff
- **State Management**: Workflow state is persisted, surviving crashes and restarts
- **Observability**: Full visibility into workflow execution via Temporal UI
- **Versioning**: Safe workflow updates without breaking in-flight executions
- **Scalability**: Workers can scale horizontally based on load

### Available Workflows

#### 1. Document Extraction Workflow (`DocumentExtractionWorkflow`)

**Queue**: `process-document-queue`

Orchestrates the complete document processing pipeline:

```python
# Workflow steps:
1. Validate document (file exists, format supported)
2. Save document metadata to database
3. Extract content (text, tables, images)
4. Chunk text using configured strategy
5. Generate embeddings (calls TextEmbeddingWorkflow)
6. Store chunks with embeddings in database
7. Cleanup temporary files
```

**Triggers**: Automatically started when a document is uploaded via API

**Activities**:

- `validate`: Validates document path and format
- `save_document_metadata`: Creates database record
- `extract_document_content`: Extracts text from PDF
- `chunk_texts_to_batched_files`: Chunks text and creates batch files
- `get_chunk_file_content_for_embedding`: Loads chunks for embedding
- `store_embedded_chunks`: Saves chunks to database
- `remove_temp_files`: Cleanup

#### 2. Text Embedding Workflow (`TextEmbeddingWorkflow`)

**Queue**: `embedding-text-queue`

Generates embeddings for text chunks using Cohere API:

```python
# Workflow steps:
1. Receive batch of texts {id: text}
2. Call embedding service with retry policy
3. Normalize embeddings to unit vectors
4. Return {id: embedding_vector}
```

**Retry Policy**: 5 attempts, 15-second intervals

**Activities**:

- `embedding_texts`: Calls Cohere API for batch embeddings

#### 3. LLM Workflow (`LLMWorkflow`)

**Queue**: `llm-queue`

Generates answers using OpenAI's GPT models:

```python
# Workflow steps:
1. Receive user prompt and system prompt
2. Call OpenAI API with configured parameters
3. Return generated text
```

**Activities**:

- `call_llm`: Calls OpenAI chat completion API

#### 4. Document Search Workflow (`DocumentSearchWorkflow`)

**Queue**: `search-on-documents-queue`

Complete RAG pipeline for semantic search:

```python
# Workflow steps:
1. Register query in database
2. Embed query (calls TextEmbeddingWorkflow)
3. Search similar chunks using vector similarity
4. Generate prompt with context
5. Generate answer (calls LLMWorkflow)
6. Save query result and chunk links
7. Format and return final result
```

**Activities**:

- `register_query`: Creates query record
- `get_chunks`: Vector similarity search
- `generate_prompt_from_template`: Builds RAG prompt
- `save_query_result`: Stores answer and chunk links
- `format_answer`: Formats final response

### Running Workers

**Development (all workers)**:

```bash
task temporal-all
```

**Production (separate processes)**:

```bash
# Terminal 1: Document extraction worker
task temporal-extract

# Terminal 2: Embedding worker
task temporal-embed

# Terminal 3: LLM worker
task temporal-llm

# Terminal 4: Search worker
task temporal-search
```

### Monitoring Workflows

Access the Temporal UI at http://localhost:8233 to:

- View running and completed workflows
- Inspect workflow history and state
- Debug failed workflows
- Replay workflows for testing
- Monitor task queue backlogs

### Task Queues Configuration

| Queue Name                  | Worker             | Purpose                          |
| --------------------------- | ------------------ | -------------------------------- |
| `process-document-queue`    | `temporal-extract` | Document extraction and chunking |
| `embedding-text-queue`      | `temporal-embed`   | Text embedding generation        |
| `llm-queue`                 | `temporal-llm`     | LLM text generation              |
| `search-on-documents-queue` | `temporal-search`  | Semantic search execution        |

## Technology Stack

### Core Technologies

- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern, high-performance web framework for building APIs
- **[Temporal.io](https://temporal.io/)**: Workflow orchestration for reliable, fault-tolerant processing
- **[PostgreSQL](https://www.postgresql.org/) + [pgvector](https://github.com/pgvector/pgvector)**: Vector database for similarity search
- **[SQLAlchemy](https://www.sqlalchemy.org/)**: Async ORM for database operations
- **Python 3.12**: Async/await, type hints, modern Python features

### AI & ML Services

- **[Cohere](https://cohere.com/)**: Text embeddings (embed-v4.0)
- **[OpenAI](https://openai.com/)**: LLM for answer generation (GPT-4)
- **[LangChain](https://www.langchain.com/)**: LLM integration framework

### Document Processing

- **[PyMuPDF](https://pymupdf.readthedocs.io/)**: PDF text extraction
- **[Chonkie](https://github.com/chonkie-ai/chonkie)**: Intelligent text chunking
- **[clean-text](https://github.com/jfilter/clean-text)**: Text normalization

### DevOps & Tools

- **[Docker Compose](https://docs.docker.com/compose/)**: Multi-container orchestration
- **[uv](https://github.com/astral-sh/uv)**: Fast Python package installer
- **[Ruff](https://github.com/astral-sh/ruff)**: Fast Python linter and formatter
- **[pytest](https://pytest.org/)**: Testing framework
- **[pre-commit](https://pre-commit.com/)**: Git hooks for code quality

## Project Structure

```
gdai/
├── api/                    # FastAPI application
│   ├── main.py            # API entry point
│   ├── deps.py            # Dependency injection
│   └── routers/           # API endpoints
│       └── v1/
│           ├── document_router.py   # Document upload/status
│           └── search_router.py     # Search endpoints
├── temporal/              # Temporal workflows and activities
│   ├── extract_document/  # Document extraction workflow
│   ├── embedding_texts/   # Embedding generation workflow
│   ├── conversational_llm/ # LLM workflow
│   └── search_on_documents/ # Search workflow
├── repositories/          # Data access layer
│   ├── models.py          # SQLAlchemy models
│   ├── pgvector_repository.py  # Vector operations
│   └── sqlalchemy.py      # Database configuration
├── embeddings/            # Embedding providers
│   ├── base_embedding.py  # Abstract interface
│   └── cohere_embedding.py # Cohere implementation
├── llms/                  # LLM providers
│   ├── base_llm.py        # Abstract interface
│   └── openai_llm.py      # OpenAI implementation
├── extractors/            # Document extractors
│   ├── base_extractor.py  # Abstract interface
│   └── pdf_extractor.py   # PDF extraction
├── chunkers/              # Text chunking strategies
│   ├── base_chunker.py    # Abstract interface
│   └── sentence_chunker.py # Sentence-based chunking
└── commons/               # Shared utilities
    ├── config.py          # Configuration management
    ├── logger.py          # Logging setup
    └── enums.py           # Enums and constants

tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests
└── e2e/                   # End-to-end tests
```

## Configuration

All configuration is managed through environment variables. See [.env.example](.env.example) for available options:

### Database Configuration

```bash
DATABASE=pgvector
PGVECTOR_HOST=localhost
PGVECTOR_PORT=5555
PGVECTOR_USER=testuser
PGVECTOR_PASSWORD=testpwd
PGVECTOR_DATABASE=vectordb
```

### Embedding Configuration

```bash
EMBEDDING_MODEL=cohere/embed-v4.0
EMBEDDING_MODEL_API_KEY=your-cohere-api-key
EMBEDDING_DIMENSION=1024
EMBEDDING_BATCH_SIZE=64
```

### LLM Configuration

```bash
LLM_MODEL=openai/gpt-4o
LLM_API_KEY=your-openai-api-key
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7
```

### Document Processing

```bash
EXTRACTOR_TMP_FOLDER=/tmp/gdai/documents
EXTRACTOR_MAX_FILE_SIZE_MB=100
```

## Development

### Running Tests

```bash
# Run all tests
task tests

# Run with coverage
pytest --cov=gdai --cov-report=html

# Run specific test file
pytest tests/unit/test_extractors.py
```

### Code Quality

```bash
# Install pre-commit hooks
task configure-dev

# Run linting manually
ruff check gdai/

# Format code
ruff format gdai/
```

### Database Management

```bash
# Reset database (WARNING: deletes all data)
task reset-db

# Setup database schema
task setup-db
```

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features and improvements:

- OpenAI embeddings support
- Image extraction with OCR
- Additional chunking strategies
- Redis caching
- Reranking support
- MCP interface
- And more...

## Documentation

- [Contributing Guidelines](docs/contributing.md) - How to contribute to GDAI
- [Code of Conduct](docs/code_of_conduct.md) - Community guidelines
- [GitHub Actions](docs/github-actions.md) - CI/CD workflows explanation
- [Codecov Setup](docs/codecov-setup.md) - Code coverage configuration
- [About](docs/about.md) - Project background and motivation
- [Changelog](CHANGELOG.md) - Version history
- [Roadmap](ROADMAP.md) - Future plans

## Troubleshooting

### Common Issues

**Workers not connecting to Temporal**:

```bash
# Check if Temporal is running
docker ps | grep temporal

# Check Temporal UI
curl http://localhost:8233
```

**Database connection errors**:

```bash
# Check PostgreSQL is running
docker ps | grep pgvector

# Test database connection
docker exec -it <container-id> psql -U testuser -d vectordb
```

**API key errors**:

- Ensure `.env` file exists and contains valid API keys
- Check that environment variables are loaded: `echo $EMBEDDING_MODEL_API_KEY`

## Community & Contributing

We welcome contributions from the community! Here's how you can help:

- **Report bugs**: Open an issue with detailed reproduction steps
- **Suggest features**: Discuss new ideas in GitHub Discussions
- **Submit PRs**: Follow our [contributing guidelines](docs/contributing.md)
- **Improve docs**: Help make the documentation better
- **Share feedback**: Tell us how you're using GDAI

Please read our [Code of Conduct](docs/code_of_conduct.md) before participating.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgments

Built with these amazing open-source projects:

- [Temporal.io](https://temporal.io/) for workflow orchestration
- [pgvector](https://github.com/pgvector/pgvector) for vector similarity search
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- And all the other dependencies that make GDAI possible

---

**Made with ❤️ for the AI community**
