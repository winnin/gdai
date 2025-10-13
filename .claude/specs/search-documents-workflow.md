# Search Documents Workflow

Performs semantic search across document chunks using vector similarity and generates RAG-based answers with source attribution.

## Location

`gdai/temporal/search_on_documents/`

## Temporal Configuration

- **Task Queue**: `search-on-documents-queue`
- **Worker Command**: `task temporal-search` or `uv run python -m gdai.temporal.search_on_documents.worker`

## Main Workflow

### DocumentSearchWorkflow

**Input**: `SearchInput`

```python
@dataclass
class SearchInput:
    query_id: str                    # Query identifier
    tenant_id: str                   # Tenant identifier
    query: str                       # User question
    document_ids: list[str]          # Documents to search in
    similarity_threshold: float      # Minimum similarity (0.0-1.0)
    top_k: int                      # Max results to return
    generate_answer: bool = True     # Whether to generate LLM answer
```

**Output**: `SearchResult`

```python
@dataclass
class SearchResult:
    query_id: str
    query: str
    answer: str | None
    chunks: list[ChunkInfo]
    total_chunks: int

@dataclass
class ChunkInfo:
    chunk_id: str
    document_id: str
    content: str
    page_number: int
    similarity_score: float
```

**Workflow Steps**:

1. `register_query()` - Saves query to database with "pending" status
2. `get_chunks()` - Performs vector similarity search
3. `generate_prompt_from_template()` - Builds LLM prompt with context
4. Executes `LLMWorkflow` (child workflow) - Generates answer
5. `save_query_result()` - Saves answer and updates status
6. `format_answer()` - Formats answer with source attribution

## Activities

### register_query

**Function**: `async def register_query(input: QueryInput) -> str`

**Purpose**: Creates query record in database with "pending" status.

**Returns**: query_id

**Timeout**: 15 seconds

---

### get_chunks

**Function**: `async def get_chunks(input: ChunkSearchParam) -> list[ChunkInfo]`

**Purpose**: Performs vector similarity search.

**Steps**:

1. Generates query embedding using EmbeddingFactory
2. Calls `PGVectorRepository.search_chunks_by_similarity_on_document_ids()`
3. Filters by similarity threshold
4. Limits to top_k results
5. Returns ranked chunks

**Similarity Calculation**: Cosine similarity using pgvector

**Timeout**: 2 minutes

---

### generate_prompt_from_template

**Function**: `async def generate_prompt_from_template(input: PromptInput) -> str`

**Purpose**: Builds LLM prompt with retrieved context.

**Template**:

```
Context from documents:
---
[Chunk 1 content from page X]
[Chunk 2 content from page Y]
---

Question: {user_question}

Please answer based on the context above. If the context doesn't contain
enough information, say so.
```

**Returns**: Formatted prompt string

**Timeout**: 10 seconds

---

### save_query_result

**Function**: `async def save_query_result(input: UpdateQueryResultInput) -> None`

**Purpose**: Updates query with answer and chunk links.

**Steps**:

1. Updates query record with answer
2. Sets status to "completed"
3. Creates QueryChunkLink records with similarity scores
4. Commits transaction

**Auditability**: Full traceability from answer to source chunks

**Timeout**: 30 seconds

---

### format_answer

**Function**: `async def format_answer(input: FormatAnswerInput) -> SearchResult`

**Purpose**: Formats final answer with source attribution.

**Output Format**:

```
Answer: [Generated answer from LLM]

Sources:
- Document: document1.pdf, Page: 5, Similarity: 0.92
- Document: document2.pdf, Page: 12, Similarity: 0.87
```

**Timeout**: 10 seconds

---

## Child Workflows

### LLMWorkflow

Calls **ConversationalLLMWorkflow** for answer generation:

```python
answer = await workflow.execute_child_workflow(
    "LLMWorkflow",
    ChatInput(
        user_prompt=formatted_prompt,
        system_prompt="You are a helpful AI assistant..."
    ),
    task_queue="llm-queue",
)
```

---

## RAG Pipeline Flow

```
1. User Query
   ↓
2. Generate Query Embedding (Cohere)
   ↓
3. Vector Similarity Search (pgvector)
   ↓
4. Filter by Threshold & Rank
   ↓
5. Build Context from Top Chunks
   ↓
6. Generate Answer (OpenAI GPT-4o)
   ↓
7. Save Answer + Source Links
   ↓
8. Return Answer with Attribution
```

---

## Configuration

### Search Parameters

```python
# Example search with default parameters
SearchInput(
    query_id="query-123",
    tenant_id="tenant-1",
    query="What is machine learning?",
    document_ids=["doc-1", "doc-2"],
    similarity_threshold=0.7,    # Only chunks with similarity >= 0.7
    top_k=5,                     # Return top 5 chunks
    generate_answer=True         # Generate LLM answer
)
```

### Similarity Threshold Guidelines

- **0.9+**: Very high similarity (almost exact match)
- **0.7-0.9**: High similarity (relevant content)
- **0.5-0.7**: Medium similarity (potentially relevant)
- **<0.5**: Low similarity (likely not relevant)

**Recommended**: 0.7 for production use

---

## Usage Example

```python
from temporalio.client import Client
from gdai.temporal.search_on_documents.schema import SearchInput

client = await Client.connect("localhost:7233")

result = await client.execute_workflow(
    "DocumentSearchWorkflow",
    SearchInput(
        query_id="query-123",
        tenant_id="tenant-1",
        query="What is RAG?",
        document_ids=["doc-1", "doc-2"],
        similarity_threshold=0.7,
        top_k=5,
        generate_answer=True
    ),
    id="search-workflow-123",
    task_queue="search-on-documents-queue",
)

print(result.answer)
# Answer: RAG (Retrieval-Augmented Generation) is...
# Sources:
# - Document: doc1.pdf, Page: 3, Similarity: 0.89
# - Document: doc2.pdf, Page: 7, Similarity: 0.82
```

---

## Multi-Tenant Isolation

- Only searches documents owned by tenant
- Query results isolated per tenant
- Embedding generation uses tenant-specific data

---

## Error Handling

- `QueryNotFoundError` - Query doesn't exist
- `EmbeddingGenerationError` - Failed to generate query embedding
- `LLMGenerationError` - Failed to generate answer
- Query status set to "failed" on errors
- Retries with exponential backoff

---

## Performance Considerations

- **Vector Index**: Uses IVFFlat index for fast similarity search
- **Batch Processing**: Embedding generation batched
- **Top-K Limiting**: Only retrieves top N results
- **Threshold Filtering**: Reduces irrelevant results

---

## Auditability Features

1. **Query Record**: Every query saved with timestamp
2. **Answer Storage**: All answers stored in database
3. **Source Links**: QueryChunkLink tracks which chunks informed answer
4. **Similarity Scores**: Preserved for transparency
5. **Full Traceability**: Can trace answer → chunks → document → page

---

## Related Specs

- [Conversational LLM Workflow](./conversational-llm-workflow.md) - Generates answers
- [Embedding Texts Workflow](./embedding-texts-workflow.md) - Generates embeddings
- [Document Management Workflow](./document-management-workflow.md) - Manages documents
- [Repositories](./repositories.md) - Vector search implementation
- [Services - Embeddings](./services.md#embeddingspy---embedding-generation)
- [Services - LLMs](./services.md#llmspy---language-model-integration)
