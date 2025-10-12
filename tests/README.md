# GDAI Test Suite

This directory contains the complete test suite for GDAI, including unit tests, integration tests, and end-to-end tests.

## 📁 Structure

````
tests/
├── conftest.py              # Shared pytest fixtures and configuration
├── mocks/                   # Mock implementations for external APIs
│   └── external_apis.py     # Cohere and OpenAI mocks
├── unit/                    # Unit tests (fast, isolated)
│   ├── services/            # Service layer tests
│   ├── repositories/        # Repository layer tests
│   └── temporal/            # Temporal activities tests
├── integration/             # Integration tests (require services)
│   └── test_document_flow.py
├── e2e/                     # End-to-end tests
└── fixtures/                # Test data and fixtures

## 🚀 Running Tests

### Prerequisites

1. **Start required services:**
   ```bash
   # Start PostgreSQL + pgvector, Temporal, and MinIO
   docker compose up -d
````

2. **Configure environment:**
   ```bash
   # Copy .env.example to .env and configure
   cp .env.example .env
   ```

### Run All Tests

```bash
# Run all tests with coverage
uv run pytest tests/ --cov=gdai --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html
```

### Run Specific Test Suites

```bash
# Unit tests only (fastest)
uv run pytest tests/unit/ -v

# Integration tests (require services)
uv run pytest tests/integration/ -v

# Specific test file
uv run pytest tests/unit/services/test_s3_storage.py -v

# Specific test class
uv run pytest tests/unit/services/test_s3_storage.py::TestS3StorageService -v

# Specific test method
uv run pytest tests/unit/services/test_s3_storage.py::TestS3StorageService::test_upload_file -v
```

### Test Options

```bash
# Run with verbose output
uv run pytest tests/ -v

# Show print statements
uv run pytest tests/ -s

# Stop on first failure
uv run pytest tests/ -x

# Run only failed tests from last run
uv run pytest tests/ --lf

# Run tests matching a pattern
uv run pytest tests/ -k "s3 or storage"

# Show slowest tests
uv run pytest tests/ --durations=10

# Parallel execution (requires pytest-xdist)
uv run pytest tests/ -n auto
```

### Coverage Reports

```bash
# Generate HTML coverage report
uv run pytest tests/ --cov=gdai --cov-report=html

# Generate terminal report with missing lines
uv run pytest tests/ --cov=gdai --cov-report=term-missing

# Generate XML report (for CI)
uv run pytest tests/ --cov=gdai --cov-report=xml

# Fail if coverage is below threshold
uv run pytest tests/ --cov=gdai --cov-fail-under=80
```

## 🧪 Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests that don't require external services.

- **Services**: S3StorageService, EmbeddingService, LLMService
- **Repositories**: PGVectorRepository
- **Activities**: Document extraction, management, embedding

**Run unit tests:**

```bash
uv run pytest tests/unit/ -v
```

### Integration Tests (`tests/integration/`)

Tests that verify multiple components working together. Require running services.

- Complete document processing flows
- Multi-tenant isolation
- Database + S3 interactions

**Run integration tests:**

```bash
# Ensure services are running
docker compose up -d

uv run pytest tests/integration/ -v
```

### E2E Tests (`tests/e2e/`)

Full end-to-end tests that simulate real user workflows.

**Run E2E tests:**

```bash
uv run pytest tests/e2e/ -v
```

## 🔧 Fixtures

### Common Fixtures (from `conftest.py`)

- `db_session`: Clean database session for each test
- `s3_storage`: S3StorageService with automatic cleanup
- `sample_tenant_id`: Test tenant ID ("test-tenant")
- `sample_pdf_path`: Generated PDF document
- `sample_text_file`: Simple text file
- `mock_cohere`: Mocked Cohere API client
- `mock_openai`: Mocked OpenAI API client

### Using Fixtures

```python
import pytest

def test_something(db_session, s3_storage, sample_tenant_id):
    """Test using multiple fixtures."""
    # db_session: AsyncSession
    # s3_storage: S3StorageService
    # sample_tenant_id: str = "test-tenant"
    pass
```

## 🐛 Debugging Tests

### Debug with pytest

```bash
# Run with Python debugger
uv run pytest tests/unit/services/test_s3_storage.py --pdb

# Drop into debugger on failure
uv run pytest tests/ --pdb --maxfail=1
```

### Debug with IDE

Most IDEs support pytest debugging. Configure your IDE to use:

- Python interpreter: `.venv/bin/python`
- Working directory: Project root
- Test runner: pytest

## 📊 Test Coverage Goals

| Component    | Target Coverage | Current |
| ------------ | --------------- | ------- |
| Services     | >90%            | -       |
| Repositories | >90%            | -       |
| Activities   | >85%            | -       |
| Workflows    | >80%            | -       |
| **Overall**  | **>80%**        | -       |

## 🎯 Writing Good Tests

### Test Naming Convention

```python
def test_<what>_<condition>_<expected>():
    """
    Examples:
    - test_upload_file_valid_input_succeeds()
    - test_get_document_not_found_raises_error()
    - test_list_documents_empty_tenant_returns_empty_list()
    """
    pass
```

### Test Structure (AAA Pattern)

```python
def test_something():
    # Arrange: Set up test data
    tenant_id = "test-tenant"
    document = create_test_document()

    # Act: Execute the code being tested
    result = service.process_document(tenant_id, document)

    # Assert: Verify the results
    assert result is not None
    assert result.status == "processed"
```

### Async Test Example

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation(db_session):
    """Test async operation."""
    result = await async_function()
    assert result is not None
```

### Mocking External APIs

```python
def test_with_mocked_cohere(mock_cohere):
    """Test using mocked Cohere API."""
    # Cohere calls are automatically mocked
    embeddings = generate_embeddings(["test text"])
    assert len(embeddings) > 0
```

## 🚨 Common Issues

### Issue: "Connection refused" errors

**Solution:** Ensure services are running:

```bash
docker compose up -d
docker compose ps  # Check status
```

### Issue: "Table does not exist" errors

**Solution:** Database fixtures handle table creation automatically. Ensure you're using the `db_session` or `db_engine` fixture.

### Issue: Tests pass locally but fail in CI

**Solution:**

1. Check that CI environment variables are set correctly
2. Ensure services are healthy in CI (check health checks)
3. Review CI logs for service startup issues

### Issue: Slow tests

**Solution:**

1. Use unit tests with mocks instead of integration tests
2. Run tests in parallel: `pytest -n auto`
3. Use `pytest --durations=10` to find slowest tests

## 📝 Test Checklist

When adding new code, ensure you have:

- [ ] Unit tests for all public methods
- [ ] Tests for error conditions
- [ ] Tests for edge cases
- [ ] Integration tests for critical flows
- [ ] Mocked external API calls
- [ ] Proper test isolation (no side effects)
- [ ] Descriptive test names
- [ ] Documentation for complex tests

## 🔗 Helpful Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

## 💡 Tips

- **Run tests frequently** during development
- **Write tests first** (TDD) when fixing bugs
- **Keep tests fast** - mock external dependencies
- **Test behavior, not implementation**
- **Use descriptive assertions** - make failures clear
- **Clean up resources** - use fixtures for setup/teardown

---

**Questions?** Check the main README or create an issue on GitHub.
