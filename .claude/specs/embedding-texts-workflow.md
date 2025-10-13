# Embedding Texts Workflow

Generates vector embeddings for text chunks using Cohere's embedding API.

## Location

`gdai/temporal/embedding_texts/`

## Temporal Configuration

- **Task Queue**: `embedding-text-queue`
- **Worker Command**: `task temporal-embed` or `uv run python -m gdai.temporal.embedding_texts.worker`

## Main Workflow

### TextEmbeddingWorkflow

**Input**: `dict[str, str]` - Mapping of chunk IDs to text content

```python
{
    "chunk-id-1": "This is the first chunk text...",
    "chunk-id-2": "This is the second chunk text...",
    ...
}
```

**Output**: `dict[str, list[float]]` - Mapping of chunk IDs to embedding vectors

```python
{
    "chunk-id-1": [0.1, 0.2, 0.3, ..., 0.9],  # 1536 dimensions
    "chunk-id-2": [0.4, 0.5, 0.6, ..., 0.8],
    ...
}
```

**Workflow Steps**:

1. Receives mapping of IDs to texts
2. Executes `embedding_texts` activity
3. Returns mapping of IDs to embeddings

## Activities

### embedding_texts

**Function**: `async def embedding_texts(content_map: dict[str, str]) -> dict[str, list[float]]`

**Purpose**: Generates embeddings for batch of texts using Cohere API.

**Steps**:

1. Extracts texts from input dictionary (preserving order)
2. Creates `EmbeddingModel` instance from settings (Cohere)
3. Calls `generate_texts_embeddings()` with batch processing
4. Maps embeddings back to original IDs
5. Returns ID-to-embedding mapping

**Batch Processing**:

- Processes texts in batches (default: 96 texts per batch)
- Configured via `EMBEDDING_BATCH_SIZE` environment variable
- Automatic retries on API failures

**Timeout**: 5 minutes

**Retry Policy**:

- Maximum attempts: 3
- Initial interval: 1 second
- Maximum interval: 30 seconds
- Backoff coefficient: 2.0

## Configuration

Uses `EmbeddingSettings` from commons:

```bash
EMBEDDING_MODEL=cohere/embed-v4.0      # Model identifier
EMBEDDING_API_KEY=your-cohere-key      # Required
EMBEDDING_DIMENSION=1536               # Vector dimension
EMBEDDING_BATCH_SIZE=96                # Batch size
EMBEDDING_MAX_TEXT_SIZE=5000           # Max characters per text
EMBEDDING_MAX_RETRIES=3                # Retry attempts
```

## Usage

### As Child Workflow

Typically called from **DocumentExtractionWorkflow**:

```python
# Prepare content map
content_to_embedding = {
    chunk["id"]: chunk["content"]
    for chunk in chunks
}

# Execute embedding workflow
embeddings = await workflow.execute_child_workflow(
    "TextEmbeddingWorkflow",
    content_to_embedding,
    task_queue="embedding-text-queue",
)

# Merge embeddings back
for chunk in chunks:
    chunk["embedding"] = embeddings.get(chunk["id"])
```

### As Standalone Workflow

```python
from temporalio.client import Client

client = await Client.connect("localhost:7233")

embeddings = await client.execute_workflow(
    "TextEmbeddingWorkflow",
    {
        "text-1": "What is machine learning?",
        "text-2": "Explain neural networks.",
    },
    id="embedding-workflow-123",
    task_queue="embedding-text-queue",
)

# embeddings = {
#     "text-1": [0.1, 0.2, ...],
#     "text-2": [0.3, 0.4, ...]
# }
```

## Vector Specifications

- **Model**: Cohere embed-v4.0
- **Dimensions**: 1536
- **Normalization**: L2 normalized (unit length)
- **Similarity Metric**: Cosine similarity (equivalent to dot product for normalized vectors)

## Error Handling

- Activity raises `EmbeddingGenerationError` on failures
- Workflow propagates exception to parent
- Automatic retries with exponential backoff
- Parent workflow sets document status to "embedding_failed"

## Integration

### Called By

- **DocumentExtractionWorkflow** - During document processing
- Can be called standalone for ad-hoc embedding generation

### Integrates With

- **CohereEmbeddingModel** (services layer) - Actual embedding generation
- **PGVectorRepository** - Stores embeddings in database

## Related Specs

- [Extract Document Workflow](./extract-document-workflow.md) - Calls this workflow
- [Search Documents Workflow](./search-documents-workflow.md) - Uses stored embeddings
- [Services - Embeddings](./services.md#embeddingspy---embedding-generation)
- [Repositories](./repositories.md) - Stores embeddings with pgvector
