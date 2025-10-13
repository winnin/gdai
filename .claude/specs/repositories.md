# Repositories - Data Access Layer

This module implements the repository pattern for data access, providing abstraction over PostgreSQL with pgvector extension for vector similarity search.

## Location

`gdai/repositories/`

## Components

### database.py - Database Connection Management

Manages async PostgreSQL connections with connection pooling.

#### DatabaseManager

Singleton manager for database engine and session factory.

**Methods:**

- `get_engine()` - Returns cached async engine or creates new one
- `_create_engine()` - Creates new SQLAlchemy async engine with pool settings
- `get_session_factory()` - Returns cached session factory or creates new one
- `create_session()` - Creates new async database session
- `dispose()` - Disposes engine and clears cache
- `health_check()` - Checks database connection health

**Configuration:**

Uses `DatabaseSettings` from commons:

- Min/max connection pool size
- Connection URL from settings
- Async PostgreSQL driver (asyncpg)

**Usage:**

```python
from gdai.repositories.database import DatabaseManager

manager = DatabaseManager()
async with manager.create_session() as session:
    # Use session for queries
    pass
```

---

### models.py - SQLAlchemy Models

Database table definitions using SQLAlchemy 2.0+ declarative syntax.

#### BaseModelMixin

Base mixin with common fields for all models.

**Fields:**

- `id: UUID` - Primary key (auto-generated UUID)
- `tenant_id: str` - Tenant identifier for multi-tenant isolation
- `created_at: datetime` - Creation timestamp
- `updated_at: datetime` - Last update timestamp

#### DocumentModel

Represents uploaded documents.

**Table:** `documents`

**Fields:**

- Inherits from `BaseModelMixin`
- `name: str` - Document filename
- `type: DocumentTypeEnum` - Document type (pdf)
- `s3_path: str` - S3 object key
- `status: DocumentStatusEnum` - Processing status
- `metadata: dict` - Additional metadata (JSON)

**Relationships:**

- `chunks: List[ChunkModel]` - One-to-many with chunks

**Indexes:**

- Primary key on `id`
- Index on `tenant_id` for filtering
- Composite index on `(tenant_id, status)` for status queries

#### ChunkModel

Represents text chunks with embeddings.

**Table:** `chunks`

**Fields:**

- Inherits from `BaseModelMixin`
- `document_id: UUID` - Foreign key to DocumentModel
- `type: ChunkTypeEnum` - Chunk type (text, image, table)
- `content: str` - Chunk text content
- `page_number: int` - Source page number
- `embedding: Vector(1536)` - pgvector embedding
- `metadata: dict` - Additional metadata (JSON)

**Relationships:**

- `document: DocumentModel` - Many-to-one with document

**Indexes:**

- Primary key on `id`
- Foreign key on `document_id`
- Index on `tenant_id`
- Vector index on `embedding` using IVFFlat for similarity search

#### QueryModel

Represents user queries and their results.

**Table:** `queries`

**Fields:**

- Inherits from `BaseModelMixin`
- `question: str` - User question
- `answer: str` - Generated answer (nullable)
- `status: QueryStatusEnum` - Processing status
- `metadata: dict` - Additional metadata (JSON)

**Relationships:**

- `query_chunk_links: List[QueryChunkLinkModel]` - Many-to-many with chunks

**Indexes:**

- Primary key on `id`
- Index on `tenant_id`
- Index on `status`

#### QueryChunkLinkModel

Links queries to relevant chunks with similarity scores.

**Table:** `query_chunk_links`

**Fields:**

- `id: UUID` - Primary key
- `query_id: UUID` - Foreign key to QueryModel
- `chunk_id: UUID` - Foreign key to ChunkModel
- `similarity_score: float` - Cosine similarity score
- `created_at: datetime` - Link creation timestamp

**Indexes:**

- Primary key on `id`
- Foreign keys on `query_id` and `chunk_id`
- Composite index on `(query_id, similarity_score)` for ranking

---

### pgvector_repository.py - Vector Repository Implementation

Main repository implementation with vector similarity search.

#### PGVectorRepository

Repository implementing CRUD operations and vector search.

**Initialization:**

```python
# With existing session
repo = PGVectorRepository(session=session)

# Create own session (use as context manager)
async with PGVectorRepository() as repo:
    documents = await repo.get_all_documents(tenant_id)
```

**Document Operations:**

- `get_all_documents(tenant_id: str) -> List[DocumentModel]`

  - Lists all documents for tenant
  - Ordered by creation date (newest first)

- `get_document(tenant_id: str, document_id: UUID) -> DocumentModel`

  - Gets document by ID
  - Raises `DocumentNotFoundError` if not found

- `insert_document(document: DocumentModel) -> DocumentModel`

  - Inserts new document to database
  - Returns inserted document with generated ID

- `delete_document(tenant_id: str, document_id: UUID) -> None`
  - Deletes document and all associated chunks
  - Uses cascade delete for chunks
  - Raises `DocumentNotFoundError` if not found

**Chunk Operations:**

- `insert_chunks(chunks: List[ChunkModel]) -> List[ChunkModel]`

  - Inserts chunks in batches (batch size from settings)
  - Returns inserted chunks with generated IDs

- `insert_batch_chunks(chunks: List[ChunkModel]) -> None`

  - Bulk insert chunks (internal method used by insert_chunks)
  - More efficient for large batches

- `get_chunks(tenant_id: str, document_id: UUID) -> List[ChunkModel]`

  - Gets all chunks for document
  - Ordered by page number and creation date

- `get_chunks_without_embedding(tenant_id: str, document_id: UUID) -> List[ChunkModel]`

  - Gets chunks that don't have embeddings yet
  - Used during document processing

- `delete_chunks(tenant_id: str, document_id: UUID) -> None`

  - Deletes all chunks for document
  - Called automatically on document deletion

- `update_chunks(chunks: List[ChunkModel]) -> None`
  - Updates existing chunks (typically to add embeddings)
  - Updates in batch

**Query Operations:**

- `insert_query(query: QueryModel) -> QueryModel`

  - Inserts new query to database
  - Returns query with generated ID

- `update_query_result(query_id: UUID, answer: str, status: QueryStatusEnum) -> None`

  - Updates query with answer and status
  - Called after LLM generates answer

- `get_query(tenant_id: str, query_id: UUID) -> QueryModel`

  - Gets query by ID
  - Raises `QueryNotFoundError` if not found

- `get_all_queries(tenant_id: str) -> List[QueryModel]`
  - Lists all queries for tenant
  - Ordered by creation date (newest first)

**Vector Search:**

- `search_chunks_by_similarity_on_document_ids(tenant_id: str, document_ids: List[UUID], embedding: List[float], threshold: float, limit: int) -> List[Tuple[ChunkModel, float]]`
  - Performs cosine similarity search across specified documents
  - Returns chunks with similarity >= threshold
  - Limited to top N results
  - Returns list of (chunk, similarity_score) tuples
  - Ordered by similarity (highest first)

**Query-Chunk Link Operations:**

- `insert_query_chunk_links(links: List[QueryChunkLinkModel]) -> None`
  - Creates links between query and relevant chunks
  - Stores similarity scores for auditability

**Context Manager:**

Repository can be used as async context manager:

```python
async with PGVectorRepository() as repo:
    documents = await repo.get_all_documents(tenant_id)
    # Session is automatically committed and closed
```

**Multi-Tenant Isolation:**

All methods enforce tenant isolation by requiring `tenant_id` parameter and filtering all queries by tenant.

---

### base_repository.py - Repository Interface

**Note:** This was the original base class but has been superseded by direct use of `PGVectorRepository`. May be used for future alternative implementations (e.g., different vector databases).

---

### sqlalchemy.py - Base Classes

**Base** - SQLAlchemy declarative base for all models

```python
from gdai.repositories.sqlalchemy import Base

# All models inherit from Base
class MyModel(Base):
    __tablename__ = "my_table"
    # ...
```

---

## Database Schema

### Tables

1. **documents** - Document metadata
2. **chunks** - Text chunks with embeddings
3. **queries** - User queries and answers
4. **query_chunk_links** - Query-to-chunk relationships

### Key Relationships

```
DocumentModel (1) ──> (N) ChunkModel
QueryModel (N) ──> (N) ChunkModel (through QueryChunkLinkModel)
```

### Indexes

**Performance-critical indexes:**

- `tenant_id` on all tables (multi-tenant filtering)
- `document_id` on chunks (foreign key lookups)
- `embedding` vector index (IVFFlat for similarity search)
- `(query_id, similarity_score)` on links (ranking results)

---

## Dependencies

- `sqlalchemy[asyncio]` - Async ORM
- `asyncpg` - Async PostgreSQL driver
- `pgvector` - Vector extension for PostgreSQL

## Related Specifications

- [Overview](./overview.md) - Project overview
- [Commons](./commons.md) - Uses settings and exceptions
- [Services](./services.md) - Used by services layer
- All workflows use repositories for data persistence
