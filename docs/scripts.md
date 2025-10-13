# GDAI Scripts Documentation

This directory contains utility scripts for development, testing, and database management.

## Available Scripts

### `dev.sh`

Development environment launcher that starts all required services and workers.

**Usage:**

```bash
./gdai/scripts/dev.sh
```

**Features:**

- Starts PostgreSQL, Temporal, and MinIO containers
- Initializes database tables
- Launches Temporal workers
- Provides health checks for all services

### `setup_db.py`

Initializes the database schema and creates required tables.

**Usage:**

```bash
uv run python gdai/scripts/setup_db.py
# Or use the task command:
task setup-db
```

**What it does:**

- Creates all SQLAlchemy models (Document, Chunk, Query)
- Sets up pgvector extension
- Creates necessary indexes

### `reset_db.py`

**⚠️ DANGER:** Drops all tables and recreates the database schema.

**Usage:**

```bash
uv run python gdai/scripts/reset_db.py
# Or use the task command:
task reset-db
```

**Warning:** This will delete ALL data in the database!

### `tests.sh`

Test runner with coverage reporting.

**Usage:**

```bash
./gdai/scripts/tests.sh
# Or use the task commands:
task tests          # All tests with coverage
task tests-unit     # Unit tests only
task tests-integration  # Integration tests
```

**Features:**

- Runs pytest with coverage
- Generates HTML and terminal reports
- Supports parallel execution

### `update_docs.sh`

Updates MkDocs documentation files from project root.

**Usage:**

```bash
./gdai/scripts/update_docs.sh
```

**What it does:**

- Copies CHANGELOG.md, ROADMAP.md, and README.md to docs/
- Adjusts internal links for MkDocs
- Prepares documentation for deployment

## Common Workflows

### Initial Setup

```bash
# 1. Start services
docker compose up -d

# 2. Initialize database
task setup-db

# 3. Start workers
task temporal-all
```

### Development Cycle

```bash
# Make changes to code
# Run tests
task tests-unit

# If database schema changed
task reset-db
```

### Clean Slate

```bash
# Stop everything
docker compose down -v

# Start fresh
docker compose up -d
task setup-db
```

## Environment Variables

All scripts respect environment variables from `.env` file. See `.env.example` for required variables.

## Troubleshooting

### Script Permission Denied

```bash
chmod +x gdai/scripts/*.sh
```

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker compose ps
docker compose logs postgres
```

### Import Errors

```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/gdai:$PYTHONPATH

# Or use uv run
uv run python gdai/scripts/setup_db.py
```
