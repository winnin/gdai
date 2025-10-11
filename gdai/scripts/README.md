# GDAI Scripts

Collection of utility scripts for development, testing, and database management.

## 📂 Available Scripts

### 🚀 Development Environment

#### `dev.sh`

Starts the complete development environment with all required services.

**Usage:**

```bash
# Start all services (infrastructure + API + workers)
./gdai/scripts/dev.sh

# Start only infrastructure services
./gdai/scripts/dev.sh infra
```

**What it does:**

1. 📦 Loads environment variables from `.env` file
2. 🐳 Starts Docker services (PostgreSQL, Temporal, MinIO)
3. 🗄️ Initializes database schema (if needed)
4. 👷 Starts Temporal workers (all workflows)
5. 🚀 Starts FastAPI server

**Services available:**

| Service           | URL                                  | Credentials        |
| ----------------- | ------------------------------------ | ------------------ |
| API Server        | http://localhost:8000                | -                  |
| API Documentation | http://localhost:8000/docs           | -                  |
| Temporal UI       | http://localhost:8233                | -                  |
| MinIO Console     | http://localhost:9001                | admin / admin      |
| PostgreSQL        | postgresql://localhost:5555/vectordb | testuser / testpwd |

**Logs:**

```bash
# Watch API logs
tail -f logs/api.log

# Watch worker logs
tail -f logs/workers.log

# Watch all logs
tail -f logs/*.log
```

**Stop services:**

Press `Ctrl+C` to stop API and workers. To stop Docker services:

```bash
docker compose down
```

**Requirements:**

- Docker and Docker Compose installed
- `.env` file configured (copy from `.env.example`)
- Python 3.12+ with uv

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
- 📦 Automatically loads `.env` file (or uses defaults if not present)

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
# 1. Copy environment file and configure
cp .env.example .env
# Edit .env with your API keys

# 2. Start development environment
./gdai/scripts/dev.sh

# This will:
# - Start Docker services
# - Setup database
# - Start workers
# - Start API
```

### During Development

```bash
# Start dev environment
./gdai/scripts/dev.sh

# In another terminal, run tests frequently
./gdai/scripts/tests.sh quick

# Run full suite before committing
./gdai/scripts/tests.sh

# Stop everything
Ctrl+C (on dev.sh terminal)
docker compose down
```

### Database Reset

```bash
# If you need to reset database schema
PYTHONPATH=. uv run python gdai/scripts/reset_db.py
PYTHONPATH=. uv run python gdai/scripts/setup_db.py

# Or restart the dev environment
docker compose down -v  # -v removes volumes
./gdai/scripts/dev.sh
```

## 📝 Notes

- All Python scripts require `PYTHONPATH` to be set
- Shell scripts automatically set `PYTHONPATH`
- Coverage reports are generated in `htmlcov/` directory
- All scripts provide colored output for better readability
- Both `dev.sh` and `tests.sh` load variables from the same `.env` file
- If `.env` doesn't exist, `tests.sh` uses safe default values for testing

## 🚀 Quick Reference

| Task                          | Command                                  |
| ----------------------------- | ---------------------------------------- |
| Start dev environment         | `./gdai/scripts/dev.sh`                  |
| Start only infrastructure     | `./gdai/scripts/dev.sh infra`            |
| Run quick tests               | `./gdai/scripts/tests.sh quick`          |
| Run all tests with coverage   | `./gdai/scripts/tests.sh`                |
| Setup database                | `uv run python gdai/scripts/setup_db.py` |
| Reset database (⚠️ dangerous) | `uv run python gdai/scripts/reset_db.py` |
| Run specific test suite       | `./gdai/scripts/tests.sh <suite>`        |
| Open coverage report          | `open htmlcov/index.html`                |
| View API logs                 | `tail -f logs/api.log`                   |
| View worker logs              | `tail -f logs/workers.log`               |
| Stop Docker services          | `docker compose down`                    |

## 🔗 Related Documentation

- [Testing Guide](../../.claude/instructions.md) - Testing conventions and best practices
- [Repository Documentation](../repositories/README.md) - Database schema details
- [Contributing Guide](../../CONTRIBUTING.md) - Development workflow
