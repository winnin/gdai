# GDAI - Claude AI Instructions

> Multi-Tenant RAG System with Temporal.io Workflows and Vector Search

**Last Updated**: 2025-10-13

---

## 🎯 What You're Working With

**GDAI** is a production-ready RAG (Retrieval-Augmented Generation) system providing:

- Multi-tenant vector storage with complete data isolation
- Document processing pipelines using Temporal.io
- Semantic search with pgvector (PostgreSQL extension)
- Auditable answers with full source traceability
- Scalable architecture for production deployment

---

## 📚 Technical Specifications

**IMPORTANT**: Detailed technical specifications are located in `.claude/specs/`:

- **[Overview](./specs/overview.md)** - Project architecture and key features
- **[Commons](./specs/commons.md)** - Settings, enums, exceptions, logging
- **[Repositories](./specs/repositories.md)** - Database models and data access
- **[Services](./specs/services.md)** - Extractors, chunkers, embeddings, LLMs, storage
- **[Workflows](./specs/)** - Temporal.io workflow specifications
- **[Testing](./specs/testing.md)** - Test strategy and structure

**When working on a specific area**, read the relevant spec file first.

---

## 🛠️ Tech Stack

| Category            | Technology              | Version/Details              |
| ------------------- | ----------------------- | ---------------------------- |
| **Language**        | Python                  | 3.12+ (type hints required)  |
| **Package Manager** | UV                      | Latest stable                |
| **Orchestration**   | Temporal.io             | Latest stable                |
| **Database**        | PostgreSQL + pgvector   | PostgreSQL 16, pgvector 0.5+ |
| **Object Storage**  | MinIO / AWS S3          | S3-compatible                |
| **Embeddings**      | Cohere embed-v4.0       | 1536 dimensions              |
| **LLM**             | OpenAI GPT-4o           | via LangChain                |
| **Web Framework**   | FastAPI                 | Async/await                  |
| **ORM**             | SQLAlchemy              | 2.0+ (async)                 |
| **Settings**        | Pydantic Settings       | Type-safe configuration      |
| **Testing**         | pytest + pytest-asyncio | 258 tests, 77% coverage      |
| **Linting**         | Ruff                    | Replaces Black, isort, flake |
| **CI/CD**           | GitHub Actions          | 4 workflows                  |

---

## 📁 Project Structure

```
gdai/
├── commons/                      # Shared utilities (READ FIRST for config)
│   ├── settings.py              # Pydantic Settings - SINGLE source of truth
│   ├── enums.py                 # All enums used in project
│   ├── logger.py                # Singleton logger (USE THIS for logging)
│   └── exceptions.py            # Custom exceptions (USE THESE for errors)
│
├── repositories/                 # Data access layer (Database operations)
│   ├── database.py              # DatabaseManager - connection pooling
│   ├── models.py                # SQLAlchemy models (DO NOT modify schema)
│   └── pgvector_repository.py  # Vector operations (USE THIS for DB queries)
│
├── services/                     # Business logic layer (External integrations)
│   ├── chunkers.py              # Text chunking strategies
│   ├── extractors.py            # PDF/document extraction
│   ├── embeddings.py            # Cohere embedding generation
│   ├── llms.py                  # OpenAI LLM integration
│   └── s3_storage.py            # S3/MinIO storage (USE get_s3_storage())
│
├── temporal/                     # Temporal.io workflows (Core orchestration)
│   ├── main.py                  # Worker launcher (START HERE for workers)
│   ├── client.py                # Temporal client utilities
│   ├── upload_file/             # File upload workflow
│   ├── extract_document/        # Document extraction workflow
│   ├── embedding_texts/         # Embedding generation workflow
│   ├── document_management/     # Document CRUD workflow
│   ├── search_on_documents/     # Semantic search workflow
│   └── conversational_llm/      # LLM chat workflow
│
└── scripts/                      # Utility scripts
    ├── setup_db.py              # Database initialization
    ├── reset_db.py              # ⚠️ DESTRUCTIVE: Drops all tables
    ├── dev.sh                   # Development launcher
    └── tests.sh                 # Test runner

tests/
├── unit/                         # 155 tests (NO external dependencies)
└── integration/                  # 103 tests (requires PostgreSQL + MinIO)
```

### Key Files You Should Know

**Configuration & Setup:**

- `pyproject.toml` - Dependencies and tool configurations (UV managed)
- `.env.example` - Environment variable template (COPY to `.env`)
- `docker-compose.yml` - Infrastructure services (PostgreSQL, Temporal, MinIO)
- `Taskfile.yml` - Task runner commands (USE `task` instead of raw commands)

**Essential Utilities:**

- `gdai/commons/settings.py` - **USE `get_settings()`** for all configuration
- `gdai/commons/logger.py` - **USE `Logger()`** for all logging
- `gdai/repositories/pgvector_repository.py` - **USE `PGVectorRepository()`** for DB
- `gdai/services/s3_storage.py` - **USE `get_s3_storage()`** for S3 operations

**Documentation:**

- `README.md` - User-facing documentation
- `.claude/specs/*.md` - Technical specifications (READ BEFORE CODING)
- `ROADMAP.md` - Planned features
- `CHANGELOG.md` - Version history

---

## ⚡ Essential Commands

### Development Setup (First Time)

```bash
# 1. Initial setup
task configure-dev              # Installs deps + pre-commit hooks
cp .env.example .env            # Copy and EDIT with your API keys

# 2. Start infrastructure
docker compose up -d            # PostgreSQL, Temporal, MinIO
task setup-db                   # Creates database tables

# 3. Start workers
task temporal-all               # All workers (recommended for dev)
```

### Daily Development

```bash
# Start services
docker compose up -d            # Infrastructure
task temporal-all               # Workers

# Run tests
task tests                      # Full test suite with coverage
task tests-unit                 # Fast unit tests only
task tests-integration          # Integration tests (requires services)
task tests-quick                # Quick run without coverage

# Code quality
uv run ruff format gdai/ tests/ # Format code (runs on commit)
uv run ruff check gdai/ tests/  # Lint code
uv run ruff check --fix         # Auto-fix linting issues

# Database
task setup-db                   # Initialize database
task reset-db                   # ⚠️ DANGER: Drops all data
```

### Package Management (UV)

```bash
uv sync --all-groups            # Install all dependencies
uv add package-name             # Add production dependency
uv add --group dev package      # Add dev dependency
uv remove package-name          # Remove dependency
uv pip list                     # List installed packages
uv tree                         # Show dependency tree
```

### Temporal Workers (Production Scaling)

```bash
task temporal-all               # All workers (dev)
task temporal-upload            # File upload worker only
task temporal-extract           # Document extraction worker only
task temporal-embed             # Embedding worker only
task temporal-llm               # LLM worker only
task temporal-search            # Search worker only
```

### Testing Commands

```bash
# Run specific tests
uv run pytest tests/unit/test_chunkers.py -v
uv run pytest tests/integration/test_repositories.py -v
uv run pytest tests/unit/test_chunkers.py::test_sentence_chunker_initialization

# Coverage reports
uv run pytest tests/ --cov=gdai --cov-report=html  # HTML report
uv run pytest tests/ --cov=gdai --cov-report=term  # Terminal report

# Debugging
uv run pytest tests/ -v         # Verbose output
uv run pytest tests/ -vv        # Very verbose
uv run pytest tests/ -s         # Show print statements
uv run pytest tests/ -x         # Stop at first failure
```

---

## 🎨 Code Style & Conventions

### Formatting Rules (Enforced by Ruff)

- **Line length**: 120 characters (hard limit)
- **Indentation**: 4 spaces (NO tabs)
- **String quotes**: Double quotes `"` (Ruff auto-converts)
- **Import sorting**: Automatic via Ruff (stdlib → third-party → local)
- **Trailing commas**: Required in multi-line structures

### Naming Conventions (MUST Follow)

```python
# Classes: PascalCase
class DocumentModel:
    pass

class PGVectorRepository:
    pass

# Functions & Methods: snake_case
def get_settings():
    pass

def extract_document():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_FILE_SIZE_MB = 100
DEFAULT_BATCH_SIZE = 96

# Private methods/variables: _leading_underscore
def _internal_helper():
    pass

_private_cache = {}

# Type variables: PascalCase with T prefix
TModel = TypeVar("TModel")
```

### Import Style (MUST Follow)

```python
# Good: Explicit imports
from gdai.commons.settings import get_settings
from gdai.commons.logger import Logger
from gdai.repositories.pgvector_repository import PGVectorRepository

# Bad: Star imports (NEVER use)
from gdai.commons import *  # ❌ FORBIDDEN

# Good: Type imports
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime

# Good: Relative imports within same module
from .schema import UploadFileInput, UploadFileOutput
from .activity import upload_file
```

### Type Hints (REQUIRED for Public APIs)

```python
# REQUIRED: All public functions must have type hints
def process_document(document_id: str, tenant_id: str) -> DocumentModel:
    """Process a document."""
    pass

# REQUIRED: Return types for async functions
async def get_document(document_id: UUID) -> DocumentModel:
    """Retrieve a document."""
    pass

# OK: Private functions can skip type hints (but encouraged)
def _helper_function(data):
    pass

# REQUIRED: Type hints for class attributes
class Config:
    max_retries: int = 3
    timeout: float = 30.0
```

### Docstring Style (Google Style)

```python
def function_name(param1: str, param2: int) -> bool:
    """Short one-line description.

    Longer description explaining what the function does, not how.
    Multiple paragraphs are OK.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        DocumentNotFoundError: When document doesn't exist

    Example:
        >>> function_name("test", 42)
        True
    """
```

### Error Handling (MUST Use Custom Exceptions)

```python
# Good: Use custom exceptions from commons.exceptions
from gdai.commons.exceptions import DocumentNotFoundError

def get_document(doc_id: str) -> DocumentModel:
    if not exists(doc_id):
        raise DocumentNotFoundError(
            message=f"Document {doc_id} not found",
            code="DOC_NOT_FOUND",
            details={"document_id": doc_id}
        )

# Bad: Generic exceptions
def get_document(doc_id: str) -> DocumentModel:
    if not exists(doc_id):
        raise Exception("Document not found")  # ❌ TOO GENERIC
```

### Logging (MUST Use Logger Singleton)

```python
# Good: Use Logger from commons
from gdai.commons.logger import Logger

logger = Logger()
logger.info("Processing document")
logger.error("Failed to process", exc_info=True)

# Bad: Direct print or logging module
print("Processing document")  # ❌ NEVER use print
import logging
logging.info("Processing")    # ❌ Use Logger() instead
```

### Async/Await Patterns

```python
# Good: Always await async calls
async def process():
    result = await async_function()
    return result

# Bad: Missing await
async def process():
    result = async_function()  # ❌ Missing await
    return result

# Good: Async context managers
async with PGVectorRepository() as repo:
    documents = await repo.get_all_documents(tenant_id)

# Good: Async iteration
async for item in async_generator():
    process(item)
```

---

## 🔀 Git & Repository Etiquette

### Branch Naming

```bash
# Feature branches
feature/add-document-tagging
feature/TICKET-123-user-authentication

# Bug fixes
fix/memory-leak-in-chunker
fix/TICKET-456-upload-timeout

# Hotfixes (production)
hotfix/critical-security-patch

# Refactoring
refactor/consolidate-settings

# Documentation
docs/update-api-documentation
```

### Commit Messages (Conventional Commits)

```bash
# Format: <type>(<scope>): <subject>

# Types:
feat:     # New feature
fix:      # Bug fix
refactor: # Code refactoring (no behavior change)
docs:     # Documentation changes
test:     # Adding/updating tests
chore:    # Maintenance tasks
perf:     # Performance improvements
style:    # Code style changes (formatting)

# Examples:
feat(upload): add support for batch file uploads
fix(search): resolve embedding dimension mismatch
refactor(settings): consolidate to Pydantic Settings
docs(readme): update installation instructions
test(repositories): add multi-tenant isolation tests
chore(deps): update dependencies to latest versions
```

**Commit Message Rules:**

1. First line: 72 characters max
2. Use imperative mood ("add" not "added")
3. No period at the end of subject
4. Body: Wrap at 72 characters
5. Include "Breaking Change:" section if applicable
6. Always add Claude Code attribution (auto-added by pre-commit)

### Pull Request Strategy

**ALWAYS create PR for main branch:**

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add my feature"

# 3. Push and create PR
git push origin feature/my-feature
# Create PR on GitHub targeting 'main'
```

**PR Title Format:** Same as commit messages

**PR Description Must Include:**

- Summary of changes
- Related issue/ticket numbers
- Testing performed
- Screenshots (if UI changes)
- Breaking changes (if any)

### Merge Strategy

- **Default**: Squash and merge (keeps history clean)
- **When to rebase**: Long-lived feature branches
- **Never force push** to main branch

---

## ⚠️ DO NOT TOUCH (Critical Rules)

### Files You Should NEVER Modify

```
❌ .github/workflows/          # GitHub Actions (unless explicitly asked)
❌ docker-compose.yml          # Infrastructure config (unless explicitly asked)
❌ pyproject.toml              # Dependencies (use UV commands instead)
❌ .pre-commit-config.yaml     # Pre-commit hooks (unless explicitly asked)
❌ alembic/versions/           # Database migrations (use alembic commands)
```

### Code You Should NEVER Change

```python
# ❌ NEVER modify database models without migration
# File: gdai/repositories/models.py
class DocumentModel(Base):
    # Changing this requires Alembic migration!
    pass

# ❌ NEVER bypass settings system
# Bad: Hardcoded config
DATABASE_URL = "postgresql://..."  # ❌ FORBIDDEN

# Good: Use settings
from gdai.commons.settings import get_settings
settings = get_settings()
db_url = settings.database.get_url()

# ❌ NEVER commit .env file
# Always use .env.example as template

# ❌ NEVER disable type checking
# Bad:
result = function()  # type: ignore  # ❌ Fix the types instead

# ❌ NEVER skip tests in CI
# Bad:
@pytest.mark.skip(reason="Broken test")  # ❌ Fix the test instead
```

### Patterns You Should NEVER Use

```python
# ❌ NEVER use bare except
try:
    risky_operation()
except:  # ❌ Too broad
    pass

# Good: Specific exceptions
try:
    risky_operation()
except (ValueError, KeyError) as e:
    logger.error(f"Operation failed: {e}")

# ❌ NEVER use mutable default arguments
def process_items(items=[]):  # ❌ DANGEROUS
    pass

# Good: Use None and create inside
def process_items(items=None):
    items = items or []

# ❌ NEVER bypass multi-tenant isolation
# Bad: Query without tenant_id filter
documents = session.query(DocumentModel).all()  # ❌ SECURITY ISSUE

# Good: Always filter by tenant
documents = session.query(DocumentModel).filter_by(tenant_id=tenant_id).all()

# ❌ NEVER commit secrets or API keys
OPENAI_API_KEY = "sk-..."  # ❌ NEVER commit this
```

### Testing Rules

```python
# ❌ NEVER skip integration tests without reason
@pytest.mark.skip  # ❌ Why?

# Good: Skip with valid reason and condition
@pytest.mark.skipif(
    not os.getenv("EMBEDDING_API_KEY"),
    reason="EMBEDDING_API_KEY not set"
)

# ❌ NEVER mock core business logic
# Bad: Mocking the thing you're testing
@patch('gdai.services.extractors.PDFExtractor.extract_document_data')
def test_extraction(mock_extract):
    mock_extract.return_value = {...}  # ❌ Not testing real code

# Good: Mock external APIs only
@patch('gdai.services.embeddings.cohere.Client')
def test_embedding(mock_cohere):
    # Testing real code, mocking external API
    pass
```

---

## 🔧 Configuration & Environment

### Environment Variables (Copy from .env.example)

**REQUIRED for basic functionality:**

```bash
# Database
DATABASE=pgvector
PGVECTOR_USER=testuser
PGVECTOR_PASSWORD=testpwd
PGVECTOR_DATABASE=vectordb
PGVECTOR_HOST=localhost
PGVECTOR_PORT=5555

# S3/MinIO
S3_ENDPOINT=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=gdai-documents

# Temporal
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
```

**OPTIONAL (tests skip if missing):**

```bash
# Embeddings (Cohere)
EMBEDDING_API_KEY=your-cohere-key     # Required for embedding tests

# LLM (OpenAI)
LLM_API_KEY=your-openai-key           # Required for LLM tests
```

### Settings Access Pattern (ALWAYS Use This)

```python
# ✅ CORRECT: Use get_settings()
from gdai.commons.settings import get_settings

settings = get_settings()
db_url = settings.database.get_url()
s3_bucket = settings.s3.s3_bucket
embedding_model = settings.embedding.embedding_model

# ❌ WRONG: Direct environment access
import os
db_url = os.getenv("PGVECTOR_HOST")  # ❌ Bypasses settings validation
```

---

## 🐛 Common Issues & Solutions

### PYTHONPATH Issues

```bash
# Symptom: ModuleNotFoundError: No module named 'gdai'

# Solution 1: Use UV (automatically sets PYTHONPATH)
uv run pytest tests/
uv run python -m gdai.temporal.main

# Solution 2: Set PYTHONPATH manually
export PYTHONPATH=/home/fabricio/projects/g-dai:$PYTHONPATH
```

### Database Connection Issues

```bash
# Symptom: Connection refused to PostgreSQL

# Check if running
docker compose ps

# View logs
docker compose logs postgres

# Restart
docker compose restart postgres

# Reset database
task reset-db
task setup-db
```

### MinIO/S3 Connection Issues

```bash
# Symptom: Connection refused to MinIO

# Check if running
docker compose ps

# View logs
docker compose logs minio

# Access MinIO UI
open http://localhost:9001
# Login: minioadmin / minioadmin
```

### Temporal Workflow Issues

```bash
# Symptom: Workflows not executing

# Check Temporal server
docker compose logs temporal

# Check worker is running
task temporal-all  # Should show "Worker started"

# View Temporal UI
open http://localhost:8233

# Check workflow status
temporal workflow list --namespace default
```

### Pre-commit Hook Failures

```bash
# Symptom: Commit rejected by pre-commit

# Run hooks manually to see what failed
pre-commit run --all-files

# Common fixes:
uv run ruff format gdai/ tests/  # Fix formatting
uv run ruff check --fix          # Fix linting issues

# Skip hooks (ONLY for emergencies)
git commit --no-verify -m "message"  # ⚠️ Use sparingly
```

---

## 📊 Project Statistics

- **Total Lines of Code**: ~10,000+
- **Test Files**: 12 files
- **Total Tests**: 258 (155 unit + 103 integration)
- **Test Coverage**: 77% (target: 80%+)
- **Source Files**: 44 files
- **Dependencies**: 30+ packages
- **Supported Python**: 3.12+
- **Active Workflows**: 6 Temporal workflows

---

## 🎯 Development Workflow (Recommended)

```bash
# 1. Start fresh session
docker compose up -d                      # Infrastructure
task temporal-all                         # Workers (separate terminal)

# 2. Create feature branch
git checkout -b feature/my-feature

# 3. Make changes
# ... edit code ...

# 4. Test as you go
task tests-unit                           # Fast feedback
task tests-integration                    # Full validation

# 5. Format & lint (runs automatically on commit)
uv run ruff format gdai/ tests/
uv run ruff check --fix

# 6. Commit with conventional commits
git add .
git commit -m "feat: add my feature"
# Pre-commit hooks run automatically

# 7. Push and create PR
git push origin feature/my-feature
# Create PR on GitHub
```

---

## 📖 Additional Resources

### Documentation

- **Main README**: `README.md` - User documentation
- **Technical Specs**: `.claude/specs/*.md` - Detailed component specs
- **Roadmap**: `ROADMAP.md` - Planned features
- **Changelog**: `CHANGELOG.md` - Version history

### Debugging Tools

- **Temporal UI**: http://localhost:8233 - Workflow debugging
- **MinIO Console**: http://localhost:9001 - Storage management
- **PostgreSQL**: `psql -h localhost -p 5555 -U testuser -d vectordb`

### External Links

- **Temporal.io Docs**: https://docs.temporal.io/
- **pgvector Docs**: https://github.com/pgvector/pgvector
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **Ruff**: https://docs.astral.sh/ruff/

---

## 🚨 Critical Reminders

1. **Always read relevant `.claude/specs/*.md` before working on a component**
2. **Never bypass multi-tenant isolation** (always filter by `tenant_id`)
3. **Use `get_settings()` for ALL configuration** (never hardcode)
4. **Use `Logger()` for ALL logging** (never use `print()`)
5. **Use custom exceptions** from `gdai.commons.exceptions`
6. **Run tests before committing** (`task tests-unit` at minimum)
7. **Follow conventional commits** for commit messages
8. **Never commit secrets** (`.env` is in `.gitignore`)
9. **Type hints required** for all public APIs
10. **Ask before modifying** database models or GitHub Actions

---

**Generated with Claude Code** | **Version**: 1.0 | **Last Updated**: 2025-10-13
