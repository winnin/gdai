# GDAI Scripts

Collection of utility scripts for development, testing, and database management.

## 📂 Available Scripts

### 🧪 Testing

#### `tests.sh`

Comprehensive test runner with multiple execution modes and coverage reporting.

**Usage:**

```bash
# Quick test (unit + api, no coverage) - ~3 seconds
./gdai/scripts/tests.sh quick

# All tests with coverage
./gdai/scripts/tests.sh

# Specific test suites
./gdai/scripts/tests.sh unit          # Unit tests only
./gdai/scripts/tests.sh integration   # Integration tests only
./gdai/scripts/tests.sh api           # API tests only

# Module-specific tests
./gdai/scripts/tests.sh commons       # Commons module
./gdai/scripts/tests.sh repositories  # Repository tests
./gdai/scripts/tests.sh llms          # LLM tests
./gdai/scripts/tests.sh embeddings    # Embedding tests

# With options
./gdai/scripts/tests.sh unit no       # No coverage (faster)
./gdai/scripts/tests.sh all yes yes   # Verbose output
```

**Features:**

- ✅ Color-coded output
- 📊 Coverage reporting (HTML + terminal)
- ⚡ Quick mode for fast feedback
- 🎯 Module-specific test execution

### 🗄️ Database Management

#### `setup_db.py`

Creates database tables and indexes for GDAI.

**Usage:**

```bash
PYTHONPATH=/home/fabricio/projects/g-dai:$PYTHONPATH uv run python gdai/scripts/setup_db.py
```

**What it does:**

- ✅ Creates pgvector extension
- ✅ Creates all tables (document, chunk, query, query_chunk_link)
- ✅ Creates HNSW index for vector similarity search

**Requirements:**

- PostgreSQL running with pgvector extension installed
- Database credentials configured in `.env` file

**Example output:**

```
✓ pgvector extension created/verified
✓ All tables created successfully!
✓ Vector index (HNSW) created successfully!

✅ Database setup completed successfully!
```

#### `reset_db.py`

**⚠️ DANGER:** Drops all tables and data from the database.

**Usage:**

```bash
PYTHONPATH=/home/fabricio/projects/g-dai:$PYTHONPATH uv run python gdai/scripts/reset_db.py
```

**What it does:**

- 🗑️ Drops all vector indexes
- 🗑️ Drops all tables and data
- ⚠️ **Requires explicit confirmation** (type 'YES')

**Safety:**

- Asks for confirmation before proceeding
- Cannot be undone - all data will be lost!

**Example:**

```bash
$ python gdai/scripts/reset_db.py

⚠️  WARNING: This will DELETE ALL TABLES and data!
Type 'YES' to confirm: YES

🗑️  Dropping all tables...
✓ Vector index dropped
✓ All tables dropped

✅ Database reset completed!

💡 Run 'python gdai/scripts/setup_db.py' to recreate tables.
```

## 🔧 Development Workflow

### Initial Setup

```bash
# 1. Setup database
PYTHONPATH=. uv run python gdai/scripts/setup_db.py

# 2. Run quick tests to verify
./gdai/scripts/tests.sh quick
```

### During Development

```bash
# Run tests frequently
./gdai/scripts/tests.sh quick

# Run full suite before committing
./gdai/scripts/tests.sh
```

### Database Reset

```bash
# If you need to reset database schema
PYTHONPATH=. uv run python gdai/scripts/reset_db.py
PYTHONPATH=. uv run python gdai/scripts/setup_db.py
```

## 📝 Notes

- All Python scripts require `PYTHONPATH` to be set
- Shell scripts automatically set `PYTHONPATH`
- Coverage reports are generated in `htmlcov/` directory
- All scripts provide colored output for better readability

## 🚀 Quick Reference

| Task                          | Command                                  |
| ----------------------------- | ---------------------------------------- |
| Run quick tests               | `./gdai/scripts/tests.sh quick`          |
| Run all tests with coverage   | `./gdai/scripts/tests.sh`                |
| Setup database                | `uv run python gdai/scripts/setup_db.py` |
| Reset database (⚠️ dangerous) | `uv run python gdai/scripts/reset_db.py` |
| Run specific test suite       | `./gdai/scripts/tests.sh <suite>`        |
| Open coverage report          | `open htmlcov/index.html`                |

## 🔗 Related Documentation

- [Testing Guide](../../.claude/instructions.md) - Testing conventions and best practices
- [Repository Documentation](../repositories/README.md) - Database schema details
- [Contributing Guide](../../CONTRIBUTING.md) - Development workflow
