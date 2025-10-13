# Conversational LLM Workflow

Generates text responses using Large Language Models (OpenAI GPT-4o) for RAG-based question answering.

## Location

`gdai/temporal/conversational_llm/`

## Temporal Configuration

- **Task Queue**: `llm-queue`
- **Worker Command**: `task temporal-llm` or `uv run python -m gdai.temporal.conversational_llm.worker`

## Main Workflow

### LLMWorkflow

**Input**: `ChatInput`

```python
@dataclass
class ChatInput:
    user_prompt: str              # User question or prompt
    system_prompt: str | None     # Optional system instructions
    temperature: float = 0.7      # Sampling temperature (0.0-2.0)
    max_tokens: int = 2000        # Maximum tokens in response
```

**Output**: `str` (Generated text response)

**Workflow Steps**:

1. Validates input parameters
2. Executes `chat_llm` activity
3. Returns generated text

**Timeout**: 5 minutes

**Retry Policy**:

- Maximum attempts: 3
- Initial interval: 2 seconds
- Maximum interval: 30 seconds
- Backoff coefficient: 2.0

---

## Activities

### chat_llm

**Function**: `async def chat_llm(input: ChatInput) -> str`

**Purpose**: Calls OpenAI API to generate text response.

**Steps**:

1. Gets LLM instance from LLMFactory (OpenAI GPT-4o)
2. Constructs messages with system and user prompts
3. Calls `llm.call_llm()` with configured parameters
4. Returns generated text

**LLM Configuration**:

- Model: OpenAI GPT-4o (configurable)
- Temperature: 0.7 (controls randomness)
- Max tokens: 2000 (maximum response length)
- Via LangChain integration

**Error Handling**:

- Raises `LLMGenerationError` on API failures
- Automatic retries with exponential backoff
- Logs all errors for debugging

**Timeout**: 5 minutes

---

## Configuration

Uses `LLMSettings` from commons:

```bash
LLM_MODEL=openai/gpt-4o           # Model identifier
LLM_API_KEY=your-openai-key       # Required
LLM_MAX_TOKENS=2000               # Default max tokens
LLM_TEMPERATURE=0.7               # Default temperature
```

---

## Usage

### As Child Workflow (RAG)

Typically called from **DocumentSearchWorkflow**:

```python
# Build context from retrieved chunks
context = "\n".join([chunk.content for chunk in chunks])

prompt = f"""
Context from documents:
{context}

Question: {user_question}

Answer based on the context above.
"""

# Call LLM workflow
answer = await workflow.execute_child_workflow(
    "LLMWorkflow",
    ChatInput(
        user_prompt=prompt,
        system_prompt="You are a helpful AI assistant that answers based on provided context.",
        temperature=0.7,
        max_tokens=2000
    ),
    task_queue="llm-queue",
)
```

### As Standalone Workflow

```python
from temporalio.client import Client
from gdai.temporal.conversational_llm.schema import ChatInput

client = await Client.connect("localhost:7233")

answer = await client.execute_workflow(
    "LLMWorkflow",
    ChatInput(
        user_prompt="What is machine learning?",
        system_prompt="You are an expert in AI.",
        temperature=0.7
    ),
    id="llm-workflow-123",
    task_queue="llm-queue",
)

print(answer)
# "Machine learning is a subset of artificial intelligence..."
```

---

## System Prompt Guidelines

### For RAG (Search Workflow)

```python
system_prompt = """
You are a helpful AI assistant that answers questions based on provided context.

Rules:
1. Only use information from the context provided
2. If the context doesn't contain enough information, say so
3. Cite specific parts of the context when possible
4. Be concise and accurate
5. Do not make up information
"""
```

### For General Chat

```python
system_prompt = """
You are a helpful AI assistant that provides accurate and helpful responses.

Rules:
1. Be concise and clear
2. Provide examples when helpful
3. Ask clarifying questions if needed
"""
```

---

## Temperature Settings

- **0.0-0.3**: Very deterministic, factual responses (recommended for RAG)
- **0.4-0.7**: Balanced creativity and consistency
- **0.8-1.0**: More creative, varied responses
- **1.1-2.0**: Highly creative, less predictable

**Recommended for GDAI RAG**: 0.5-0.7

---

## Token Management

### Max Tokens Calculation

```python
# Estimate tokens (rough approximation)
# 1 token ≈ 4 characters for English text

context_tokens = len(context) // 4
question_tokens = len(question) // 4
input_tokens = context_tokens + question_tokens

# Reserve tokens for response
max_response_tokens = 2000
max_input_tokens = 8000  # GPT-4o limit is higher, but be conservative

if input_tokens > max_input_tokens:
    # Truncate context or reduce chunk count
    pass
```

### Token Limits by Model

- **GPT-4o**: 128k context window
- **GPT-4o-mini**: 128k context window
- **GPT-3.5-turbo**: 16k context window

**GDAI Default**: Uses GPT-4o with 8k input + 2k output budget

---

## Error Handling

### Common Errors

1. **Rate Limit Exceeded**

   - Retry with exponential backoff
   - Consider using GPT-4o-mini for high-volume

2. **Context Too Long**

   - Reduce number of chunks (lower top_k)
   - Truncate chunk content
   - Use shorter system prompt

3. **API Key Invalid**

   - Check `LLM_API_KEY` environment variable
   - Verify API key is active

4. **Model Not Available**
   - Check model name in `LLM_MODEL`
   - Verify account has access to model

### Error Response

On failure, raises `LLMGenerationError`:

```python
raise LLMGenerationError(
    message="Failed to generate LLM response",
    code="LLM_ERROR",
    details={"error": str(e)}
)
```

---

## Integration

### Called By

- **DocumentSearchWorkflow** - For RAG-based answers
- Can be called standalone for general chat

### Integrates With

- **OpenAIModel** (services layer) - Actual LLM calls via LangChain
- **DocumentSearchWorkflow** - Provides context for RAG

---

## Cost Considerations

### OpenAI Pricing (as of 2024)

- **GPT-4o**: $5/1M input tokens, $15/1M output tokens
- **GPT-4o-mini**: $0.15/1M input tokens, $0.60/1M output tokens

### Cost Optimization

1. **Use GPT-4o-mini for simple queries**

   - 97% cheaper than GPT-4o
   - Similar quality for factual Q&A

2. **Reduce top_k in search**

   - Fewer chunks = less input tokens
   - Still maintain quality

3. **Shorter system prompts**

   - Every character counts toward token limit

4. **Cache results**
   - Store query-answer pairs
   - Return cached answers for identical queries

---

## Related Specs

- [Search Documents Workflow](./search-documents-workflow.md) - Main caller for RAG
- [Services - LLMs](./services.md#llmspy---language-model-integration) - LLM implementation
- [Commons - Settings](./commons.md#llmsettings) - LLM configuration
