# Testing Strategy & Structure

Comprehensive testing strategy for GDAI with unit, integration, and end-to-end tests.

## Test Statistics

- **Total Tests**: 258
- **Unit Tests**: 155 (100% passing)
- **Integration Tests**: 103 (100% passing, 36 skipped without API keys)
- **Test Coverage**: 77%
- **CI/CD**: Automated via GitHub Actions

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests (no external dependencies)
│   ├── test_chunkers.py     # Text chunking tests
│   ├── test_config.py       # Configuration tests
│   ├── test_enums.py        # Enum validation tests
│   ├── test_extractors.py   # Document extraction tests
│   └── test_logger.py       # Logging tests
├── integration/             # Integration tests (requires services)
│   ├── test_document_flow.py
│   ├── test_document_management_activities.py
│   ├── test_embeddings.py   # Requires EMBEDDING_API_KEY
│   ├── test_extract_activities.py
│   ├── test_llms.py         # Requires LLM_API_KEY
│   ├── test_pgvector_repository.py
│   ├── test_repositories.py
│   ├── test_s3_storage.py
│   └── test_upload_file_workflow.py
└── e2e/                     # End-to-end workflow tests
    ├── test_chunk_embedding.py
    ├── test_embedding.py
    ├── test_extraction.py
    ├── test_llm.py
    └── test_search.py
```

## Test Categories

### Unit Tests (155 tests)

**Purpose**: Test individual components in isolation

**Characteristics**:

- No external dependencies (no DB, S3, APIs)
- Fast execution (<1 second per test)
- Mocked external calls
- 100% passing

**Key Test Files**:

#### test_chunkers.py (30 tests)

- BaseChunker initialization and abstract methods
- DocumentTextChunkerBySentence chunking logic
- Text cleaning and normalization
- ChunkerFactory pattern
- Edge cases (empty strings, unicode, special chars)

#### test_extractors.py (31 tests)

- PDFExtractor text extraction
- Table extraction from PDFs
- Image extraction from PDFs
- ExtractorFactory pattern
- Error handling for invalid files

#### test_enums.py (11 tests)

- DocumentStatusEnum values
- DocumentTypeEnum values
- ChunkTypeEnum values
- QueryStatusEnum values

#### test_logger.py (27 tests)

- Logger singleton pattern
- ColorFormatter functionality
- ModulePathFilter enrichment
- Log level filtering
- Exception logging

#### test_config.py (50 tests)

- DatabaseSettings validation
- S3Settings validation
- EmbeddingSettings validation
- LLMSettings validation
- Settings loading from environment

**Running Unit Tests**:

```bash
task tests-unit
# or
uv run pytest tests/unit/ -v
```

---

### Integration Tests (103 passing, 36 skipped)

**Purpose**: Test components working together with real services

**Requirements**:

- PostgreSQL + pgvector running
- MinIO/S3 running
- Optional: API keys for full test suite

**Characteristics**:

- Requires Docker services
- Moderate execution time (30s-2min)
- Real database/storage operations
- Transaction rollback for cleanup

**Key Test Files**:

#### test_repositories.py (22 tests)

- PGVectorRepository CRUD operations
- Vector similarity search
- Multi-tenant isolation
- Query-chunk linking
- Transaction management

#### test_s3_storage.py (21 tests)

- S3StorageService upload/download
- Tenant isolation in S3
- File existence checks
- File listing
- Error handling

#### test_pgvector_repository.py (15 tests)

- Direct repository usage
- Async context manager
- Batch operations
- Vector operations

#### test_document_flow.py (3 tests)

- End-to-end document processing
- Upload → Extract → Embed flow
- Multi-tenant document isolation

#### test_extract_activities.py (15 tests)

- Document validation activity
- Metadata saving activity
- Content extraction activity
- Chunking activity
- Error handling

#### test_document_management_activities.py (7 tests)

- List documents activity
- Get document activity
- Delete document activity
- Get chunks activity
- S3 integration

#### test_upload_file_workflow.py (20 tests)

- File upload workflow
- File object upload workflow
- Delete file workflow
- Check file exists workflow
- List files workflow
- Multi-tenant isolation

**Running Integration Tests**:

```bash
# Start services first
docker compose up -d
task setup-db

# Run tests
task tests-integration
# or
uv run pytest tests/integration/ -v
```

---

### API-Dependent Tests (36 tests)

**Requirements**: Valid API keys in environment

#### test_embeddings.py (24 tests)

- Requires: `EMBEDDING_API_KEY` (Cohere)
- EmbeddingModel initialization
- Batch embedding generation
- Vector normalization
- EmbeddingFactory pattern
- Error handling for API failures

#### test_llms.py (27 tests)

- Requires: `LLM_API_KEY` (OpenAI)
- LLMModel initialization
- Text generation
- System prompt handling
- Temperature control
- LLMFactory pattern
- Error handling for API failures

**Running with API Keys**:

```bash
# Set API keys
export EMBEDDING_API_KEY=your-cohere-key
export LLM_API_KEY=your-openai-key

# Run all tests
task tests
```

**Without API Keys**:

- Tests are automatically skipped
- CI pipeline still passes
- Marked with `@pytest.mark.skipif`

---

### End-to-End Tests (e2e/)

**Purpose**: Test complete workflows from start to finish

**Characteristics**:

- Requires all services running
- Requires API keys
- Longest execution time
- Tests real-world scenarios

**Test Files**:

#### test_extraction.py

- Upload file → Extract → Store chunks
- Complete document processing pipeline

#### test_embedding.py

- Extract document → Generate embeddings
- Complete embedding pipeline

#### test_chunk_embedding.py

- Full chunking + embedding workflow

#### test_search.py

- Document upload → Extract → Search → RAG
- Complete search pipeline with LLM

#### test_llm.py

- LLM workflow with context
- RAG-based question answering

---

## Test Fixtures

### conftest.py

**Global Fixtures**:

```python
@pytest.fixture
def test_settings():
    """Provides test configuration settings"""
    return get_settings()

@pytest.fixture
def event_loop():
    """Provides async event loop for async tests"""
    return asyncio.get_event_loop()

@pytest.fixture
async def db_engine():
    """Creates test database engine"""
    # Creates engine with test settings
    yield engine
    # Cleanup

@pytest.fixture
async def db_session(db_engine):
    """Provides database session for tests"""
    async with create_session() as session:
        yield session
        await session.rollback()  # Rollback after test

@pytest.fixture
def sample_tenant_id():
    """Provides test tenant ID"""
    return "test-tenant-123"

@pytest.fixture
async def cleanup_database(db_session):
    """Cleans up database after tests"""
    # Delete test data
    await db_session.execute(delete(DocumentModel))
    await db_session.commit()
```

---

## Running Tests

### All Tests

```bash
task tests
# Runs unit + integration + coverage report
```

### By Category

```bash
task tests-unit          # Unit tests only (fast)
task tests-integration   # Integration tests only
task tests-quick         # All tests without coverage
```

### Specific Test File

```bash
uv run pytest tests/unit/test_chunkers.py -v
uv run pytest tests/integration/test_repositories.py -v
```

### Specific Test

```bash
uv run pytest tests/unit/test_chunkers.py::test_sentence_chunker_initialization -v
```

### With Coverage

```bash
uv run pytest tests/ --cov=gdai --cov-report=html
# Opens htmlcov/index.html in browser
```

### Verbose Output

```bash
uv run pytest tests/ -v          # Verbose
uv run pytest tests/ -vv         # Very verbose
uv run pytest tests/ -s          # Show print statements
```

---

## CI/CD Testing

### GitHub Actions Workflows

#### ci.yml - Main CI Pipeline

```yaml
runs-on: ubuntu-latest
services:
  postgres:
    image: pgvector/pgvector:pg16
  minio:
    image: minio/minio

steps:
  - Checkout code
  - Setup Python 3.12
  - Install UV
  - Install dependencies
  - Run unit tests
  - Run integration tests (no API keys)
  - Generate coverage report
  - Upload to Codecov
```

**Triggers**:

- Push to any branch
- Pull requests to main

**Status**: Must pass for PR merge

#### pr-checks.yml - PR Validation

```yaml
steps:
  - Lint with Ruff
  - Format check with Ruff
  - Type check with mypy
  - Security scan with Bandit
  - Run tests with coverage
  - Coverage threshold check (70%)
```

**Coverage Enforcement**: PR fails if coverage drops below 70%

---

## Test Development Guidelines

### Writing Unit Tests

```python
def test_feature_name():
    """Test description of what is being tested"""
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

### Writing Integration Tests

```python
@pytest.mark.asyncio
async def test_feature_integration(db_session, sample_tenant_id):
    """Test description requiring database"""
    # Arrange
    repo = PGVectorRepository(session=db_session)
    document = create_test_document(tenant_id=sample_tenant_id)

    # Act
    await repo.insert_document(document)
    result = await repo.get_document(sample_tenant_id, document.id)

    # Assert
    assert result.id == document.id

    # Cleanup handled by fixture
```

### Skipping Tests Without API Keys

```python
@pytest.mark.skipif(
    not os.getenv("EMBEDDING_API_KEY"),
    reason="EMBEDDING_API_KEY not set"
)
@pytest.mark.asyncio
async def test_embedding_generation():
    """Test requiring Cohere API key"""
    # Test code
```

---

## Mocking External Services

### Mock S3 Operations

```python
from unittest.mock import Mock, patch

@patch('gdai.services.s3_storage.boto3.client')
def test_s3_upload(mock_boto_client):
    mock_s3 = Mock()
    mock_boto_client.return_value = mock_s3

    # Test upload
    storage = S3StorageService(settings)
    storage.upload_file("tenant-1", "file.pdf", "file.pdf")

    mock_s3.upload_file.assert_called_once()
```

### Mock API Calls

```python
@patch('gdai.services.embeddings.cohere.Client')
def test_embedding_api(mock_cohere):
    mock_client = Mock()
    mock_client.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
    mock_cohere.return_value = mock_client

    # Test embedding
    model = CohereEmbeddingModel(...)
    embeddings = model.generate_texts_embeddings(["test"])

    assert len(embeddings) == 1
```

---

## Coverage Goals

### Current Coverage: 77%

**Target Coverage by Module**:

- Commons: 90%+
- Repositories: 85%+
- Services: 80%+
- Temporal workflows: 75%+
- Overall: 80%+

**Coverage Reports**:

```bash
# Terminal report
uv run pytest tests/ --cov=gdai --cov-report=term

# HTML report (detailed)
uv run pytest tests/ --cov=gdai --cov-report=html
open htmlcov/index.html

# XML report (for CI)
uv run pytest tests/ --cov=gdai --cov-report=xml
```

---

## Troubleshooting Tests

### Database Connection Errors

```bash
# Check PostgreSQL is running
docker compose ps
docker compose logs postgres

# Reset database
task reset-db
task setup-db
```

### S3 Connection Errors

```bash
# Check MinIO is running
docker compose ps
docker compose logs minio

# Access MinIO UI
open http://localhost:9001
# Login: minioadmin / minioadmin
```

### Import Errors

```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/gdai:$PYTHONPATH

# Or use UV (automatically sets PYTHONPATH)
uv run pytest tests/
```

### Async Test Errors

```python
# Always use @pytest.mark.asyncio
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result
```

---

## Related Specs

- [Overview](./overview.md) - Project overview
- [Commons](./commons.md) - Test configuration and settings
- [Repositories](./repositories.md) - Repository tests
- [Services](./services.md) - Service tests
- All workflow specs - Workflow and activity tests
