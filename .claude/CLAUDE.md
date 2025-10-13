# GDAI Project - Claude AI Context

> Multi-Tenant Vector Store with Auditable Semantic Search using Temporal.io and RAG

---

## 📋 Project Overview

**GDAI** is a production-ready RAG (Retrieval-Augmented Generation) system that provides:

- **Multi-tenant vector storage** with complete data isolation
- **Document processing pipelines** using Temporal.io workflows
- **Semantic search** with pgvector (PostgreSQL extension)
- **Auditable answers** with full source traceability
- **Scalable architecture** ready for production deployment

### Tech Stack

| Category            | Technology              | Purpose                                 |
| ------------------- | ----------------------- | --------------------------------------- |
| **Language**        | Python 3.12+            | Modern Python with type hints           |
| **Package Manager** | UV                      | Fast dependency management              |
| **Orchestration**   | Temporal.io             | Workflow engine for document processing |
| **Database**        | PostgreSQL + pgvector   | Vector storage with SQL                 |
| **Object Storage**  | MinIO / AWS S3          | Document storage                        |
| **Embeddings**      | Cohere embed-v4.0       | Text embeddings (1536 dimensions)       |
| **LLM**             | OpenAI GPT-4o           | Answer generation                       |
| **Settings**        | Pydantic Settings       | Type-safe configuration                 |
| **Testing**         | pytest + pytest-asyncio | Async testing framework                 |
| **CI/CD**           | GitHub Actions          | Automated testing and deployment        |

---

## 📁 Project Structure

```
gdai/
├── commons/                      # Shared utilities and configuration
│   ├── settings.py              # Pydantic Settings (unified config)
│   ├── enums.py                 # Project enums
│   ├── logger.py                # Logging utilities
│   └── exceptions.py            # Custom exceptions
│
├── repositories/                 # Data access layer
│   ├── database.py              # DatabaseManager (async connection pool)
│   ├── models.py                # SQLAlchemy models (Document, Chunk, Query)
│   └── pgvector_repository.py  # Vector operations
│
├── services/                     # Business logic layer
│   ├── chunkers.py              # Document chunking strategies
│   ├── extractors.py            # Document extraction (PDF, etc)
│   ├── embeddings.py            # Embedding generation (Cohere)
│   ├── llms.py                  # LLM interactions (OpenAI)
│   └── s3_storage.py            # S3/MinIO storage service
│
├── temporal/                     # Temporal.io workflows
│   ├── main.py                  # Worker launcher (all workflows)
│   ├── client.py                # Temporal client utilities
│   ├── upload_file/             # File upload to S3 workflow
│   ├── extract_document/        # Document extraction workflow
│   ├── embedding_texts/         # Text embedding workflow
│   ├── document_management/     # Document CRUD workflow
│   ├── search_on_documents/     # Semantic search workflow
│   └── conversational_llm/      # RAG chat workflow
│
└── scripts/                      # Utility scripts
    ├── setup_db.py              # Database initialization
    ├── reset_db.py              # Database reset
    ├── dev.sh                   # Development environment launcher
    └── tests.sh                 # Test runner with coverage

tests/
├── unit/                         # Unit tests (155 tests)
│   ├── test_chunkers.py
│   ├── test_extractors.py
│   ├── test_enums.py
│   └── test_logger.py
│
└── integration/                  # Integration tests (109 tests)
    ├── test_repositories.py
    ├── test_s3_storage.py
    ├── test_document_flow.py
    ├── test_extract_activities.py
    ├── test_document_management_activities.py
    ├── test_upload_file_workflow.py  # File upload workflow tests
    ├── test_embeddings.py       # Requires EMBEDDING_API_KEY
    └── test_llms.py             # Requires LLM_API_KEY
```

---

## ⚡ Most Used Commands

### Development Setup

```bash
# Initial setup (run once)
task configure-dev              # Install deps + setup pre-commit hooks
cp .env.example .env            # Copy environment template
# Edit .env with your API keys

# Start infrastructure
docker compose up -d            # PostgreSQL, Temporal, MinIO
task setup-db                   # Create database tables

# Start workers
task temporal-all               # All workers (recommended)
task temporal-upload            # Only file upload worker
task temporal-extract           # Only extraction worker
task temporal-embed             # Only embedding worker
task temporal-llm               # Only LLM worker
task temporal-search            # Only search worker
```

### Testing

```bash
# Run tests
task tests                      # All tests with coverage
task tests-unit                 # Unit tests only (fast)
task tests-integration          # Integration tests (requires services)
task tests-quick                # Quick run (no coverage)

# Direct pytest
uv run pytest tests/unit/ -v                    # Unit tests verbose
uv run pytest tests/integration/ -v             # Integration tests
uv run pytest tests/ --cov=gdai --cov-report=html  # With coverage report
```

### Database Management

```bash
task setup-db                   # Initialize database (create tables)
task reset-db                   # ⚠️ DANGER: Drop and recreate all tables
uv run python gdai/scripts/setup_db.py    # Direct setup script
```

### Development Environment

```bash
task dev                        # Start everything (infra + workers + API)
task dev-infra                  # Only infrastructure services

# Manual approach
docker compose up -d            # Start services
task temporal-all               # Start workers in terminal 1
# Your app runs in terminal 2
```

### Code Quality

```bash
# Linting and formatting
uv run ruff check gdai/ tests/              # Check code
uv run ruff format gdai/ tests/             # Format code
uv run ruff check gdai/ tests/ --fix        # Auto-fix issues

# Pre-commit (runs automatically on commit)
pre-commit run --all-files                  # Manual run
```

### Package Management

```bash
# UV commands
uv sync --all-groups            # Install all dependencies
uv add package-name             # Add new dependency
uv add --group dev package      # Add dev dependency
uv pip list                     # List installed packages
uv tree                         # Show dependency tree
```

---

## 🔧 Environment Variables

### Required Variables

```bash
# Database (PostgreSQL + pgvector)
DATABASE=pgvector
PGVECTOR_USER=testuser
PGVECTOR_PASSWORD=testpwd
PGVECTOR_DATABASE=vectordb
PGVECTOR_HOST=localhost
PGVECTOR_PORT=5555
PGVECTOR_MIN_POOL_CONNECTIONS=2
PGVECTOR_MAX_POOL_CONNECTIONS=10

# S3/MinIO Storage
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=gdai-documents
S3_REGION=us-east-1
S3_USE_SSL=false

# Embedding (Cohere)
EMBEDDING_MODEL=cohere/embed-v4.0
EMBEDDING_API_KEY=your-cohere-api-key    # ⚠️ Required for embeddings
EMBEDDING_DIMENSION=1536
EMBEDDING_BATCH_SIZE=96
EMBEDDING_MAX_TEXT_SIZE=5000
EMBEDDING_MAX_RETRIES=3

# LLM (OpenAI)
LLM_MODEL=openai/gpt-4o
LLM_API_KEY=your-openai-api-key          # ⚠️ Required for LLM
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7

# Document Extraction
EXTRACTOR_TMP_FOLDER=/tmp/gdai
EXTRACTOR_MAX_FILE_SIZE_MB=100
EXTRACTOR_MAX_RETRIES=3

# Temporal.io
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_TASK_QUEUE=gdai-task-queue

# Logging
GDAI_LOG_LEVEL=INFO
GDAI_LOG_FORMAT=[%(asctime)s] [GDAI] [%(levelname)s]: %(message)s
```

---

## 🔄 Temporal.io Workflows

### Available Workflows

| Workflow               | Queue                       | Purpose                              |
| ---------------------- | --------------------------- | ------------------------------------ |
| **UploadFile**         | `upload-file-queue`         | Upload files to S3/MinIO storage     |
| **ExtractDocument**    | `process-document-queue`    | Extract text/metadata from documents |
| **EmbedTexts**         | `embedding-text-queue`      | Generate embeddings for text chunks  |
| **DocumentManagement** | `document-management-queue` | CRUD operations for documents        |
| **SearchDocuments**    | `search-on-documents-queue` | Semantic search across documents     |
| **ConversationalLLM**  | `llm-queue`                 | RAG-based conversational answers     |

### Starting Workers

```bash
# All workers in one process (recommended for development)
task temporal-all

# Individual workers (for scaling in production)
task temporal-upload     # Handles file uploads to S3
task temporal-extract    # Handles document extraction
task temporal-embed      # Handles embedding generation
task temporal-llm        # Handles LLM queries
task temporal-search     # Handles search operations
```

### Workflow Execution Flow

```
1. Document Upload → S3/MinIO
2. Trigger ExtractDocument workflow
   ├─ Download from S3
   ├─ Extract text/metadata (PDF, etc)
   ├─ Save to database
   └─ Trigger EmbedTexts workflow
3. EmbedTexts workflow
   ├─ Chunk text into semantic units
   ├─ Generate embeddings (Cohere)
   └─ Store vectors in pgvector
4. SearchDocuments workflow
   ├─ Generate query embedding
   ├─ Vector similarity search
   └─ Return ranked results
5. ConversationalLLM workflow
   ├─ Search relevant chunks
   ├─ Build context
   ├─ Generate answer (OpenAI)
   └─ Return answer + sources
```

---

## 🧪 Testing Strategy

### Test Organization

- **Unit Tests** (155 tests): Pure logic, no external dependencies
- **Integration Tests** (103 tests): Requires PostgreSQL + MinIO
- **API Tests** (36 tests): Requires Cohere + OpenAI API keys

### Running Tests in CI

Tests run automatically on every push via GitHub Actions:

```yaml
Workflows:
├── ci.yml           # Code quality + unit + integration tests
├── pr-checks.yml    # PR validation + coverage + security
├── security.yml     # Vulnerability scanning + CodeQL
└── docs.yml         # Documentation build + deployment
```

### Test Coverage

```bash
# Run with coverage report
task tests                                           # HTML + terminal report
uv run pytest tests/ --cov=gdai --cov-report=html   # Opens in browser

# Coverage targets
# Unit tests: 100% passing
# Integration tests: 103 passing (without API keys)
# Integration tests: 139 passing (with API keys)
```

---

## 🗄️ Database Schema

### Core Models

```python
# Document Model
class DocumentModel:
    id: UUID                    # Primary key
    tenant_id: str              # Multi-tenant isolation
    name: str                   # Filename
    type: DocumentTypeEnum      # pdf, txt, etc
    s3_path: str               # S3 object key
    status: DocumentStatusEnum  # processed, failed, etc
    created_at: datetime
    updated_at: datetime

# Chunk Model (Text embeddings)
class ChunkModel:
    id: UUID
    document_id: UUID           # Foreign key to Document
    tenant_id: str
    content: str               # Chunk text
    type: ChunkTypeEnum        # text, table, image
    page_number: int
    embedding: Vector(1536)    # pgvector type
    created_at: datetime

# Query Model (Search history)
class QueryModel:
    id: UUID
    tenant_id: str
    question: str
    answer: str
    status: QueryStatusEnum
    created_at: datetime
```

### Key Indexes

- `tenant_id` on all tables (multi-tenant isolation)
- `embedding` vector index (IVFFlat for similarity search)
- `document_id` foreign keys
- Composite indexes for common queries

---

## 🔐 Security & Secrets

### GitHub Actions Secrets

Configure in: **Settings → Secrets and variables → Actions**

| Secret Name         | Required | Purpose                               |
| ------------------- | -------- | ------------------------------------- |
| `EMBEDDING_API_KEY` | Optional | Cohere API for full integration tests |
| `LLM_API_KEY`       | Optional | OpenAI API for full integration tests |
| `CODECOV_TOKEN`     | Optional | Coverage reporting                    |

**Note**: Without API keys, 36 tests will be skipped but CI will still pass.

---

## 🔧 Common Issues & Solutions

### Issue: `ModuleNotFoundError: No module named 'gdai'`

**Solution**: Set PYTHONPATH

```bash
export PYTHONPATH=/path/to/gdai:$PYTHONPATH
# Or use: uv run python (automatically sets PYTHONPATH)
```

### Issue: `ModuleNotFoundError: No module named 'pydantic_settings'`

**Solution**: Reinstall dependencies

```bash
uv sync --all-groups --frozen
```

### Issue: Database connection failed

**Solution**: Check PostgreSQL is running

```bash
docker compose ps                    # Check status
docker compose logs postgres         # Check logs
psql -h localhost -p 5555 -U testuser -d vectordb  # Test connection
```

### Issue: MinIO connection refused

**Solution**: Check MinIO is running

```bash
docker compose ps                    # Check status
curl http://localhost:9000/minio/health/live  # Health check
```

### Issue: Temporal workflows not executing

**Solution**: Check Temporal server and workers

```bash
# Check Temporal server
docker compose logs temporal

# Check worker logs
task temporal-all  # Should show "Worker started successfully"

# Verify in Temporal UI
open http://localhost:8233
```

---

## 📚 Key Files to Know

### Configuration

- `pyproject.toml` - Project dependencies and tool configs
- `.env` - Environment variables (not in git)
- `.env.example` - Environment template
- `docker-compose.yml` - Infrastructure services

### Documentation

- `README.md` - Main documentation
- `SPEC.md` - Technical specification (all classes/methods)
- `ROADMAP.md` - Future features
- `CHANGELOG.md` - Version history
- `.github/GITHUB_SETUP.md` - CI/CD setup guide

### CI/CD

- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/pr-checks.yml` - PR validation
- `.github/workflows/security.yml` - Security scanning
- `.github/workflows/docs.yml` - Documentation deployment

---

## 📝 Code Style & Conventions

### Formatting & Linting

- **Ruff**: Modern Python linter/formatter (replaces Black + isort + flake8)
- **Line length**: 120 characters
- **Import sorting**: Automatic with Ruff
- **Type hints**: Required for public APIs

### Naming Conventions

- **Classes**: PascalCase (`DocumentModel`, `PGVectorRepository`)
- **Functions**: snake_case (`get_settings`, `extract_document`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_FILE_SIZE_MB`)
- **Private methods**: `_private_method`

### Docstring Style

```python
def function_name(param: str) -> str:
    """Short description in one line.

    Longer description if needed. Explain what the function does,
    not how it does it.

    Args:
        param: Description of parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param is invalid
    """
```

---

## 🔄 Recent Changes

### Latest Refactorings

1. **Removed config.py** (commit 131d0d9)

   - Consolidated to Pydantic Settings only
   - Removed 234 lines of duplicate code
   - Modern type-safe configuration

2. **Consolidated GitHub Actions** (commit 4bfb5d7)

   - Removed duplicate workflows (tests.yml, pre-commit.yml)
   - Created focused workflows (ci.yml, pr-checks.yml, security.yml, docs.yml)
   - Reduced workflow code by 150 lines

3. **Fixed CI Issues** (commits d2d33c7, 2864a9b, ab6b5c7, b2806d9)
   - MinIO container startup
   - Missing dependencies (pydantic-settings, ruff)
   - PYTHONPATH configuration
   - Code formatting

---

## 🚀 Development Workflow

### Typical Development Cycle

```bash
# 1. Start fresh
docker compose down -v                    # Clean slate
docker compose up -d                      # Start services
task setup-db                             # Initialize DB

# 2. Make changes to code
# ... edit files ...

# 3. Run tests
task tests-unit                           # Quick feedback
task tests-integration                    # Full validation

# 4. Format & lint
uv run ruff format gdai/ tests/           # Format
uv run ruff check gdai/ tests/ --fix      # Fix issues

# 5. Commit
git add .
git commit -m "feat: your feature"        # Pre-commit hooks run automatically

# 6. Push
git push origin your-branch               # CI runs automatically
```

### Branch Strategy

- `main` - Production-ready code
- `develop` - Integration branch (if used)
- `feature/*` - Feature branches
- `fix/*` - Bug fixes

---

## 📖 Getting Help

### Resources

- **Documentation**: See `README.md` and `SPEC.md`
- **Examples**: Check `tests/integration/` for usage examples
- **Temporal UI**: http://localhost:8233 for workflow debugging
- **Logs**: `docker compose logs -f <service>` for service logs

### Debug Mode

```bash
# Enable debug logging
export GDAI_LOG_LEVEL=DEBUG

# Run with verbose output
uv run python -m gdai.temporal.main --verbose
```

---

## 📊 Project Stats

- **Source Files**: 44 files
- **Test Files**: 12 files (258 tests total)
- **Lines of Code**: ~10,000+ lines
- **Dependencies**: 30+ packages
- **Supported Python**: 3.12+
- **Test Coverage**: 80%+ target

---

**Last Updated**: 2025-10-13
**Claude Code Version**: Compatible with Claude Code v1.0+
