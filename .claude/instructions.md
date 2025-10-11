# Claude Code - Instruções de Autonomia para GDAI

## 🎯 Objetivo Deste Arquivo

Definir permissões, limites e preferências para que Claude trabalhe de forma autônoma e eficiente, sem pedidos desnecessários de confirmação.

---

## ✅ Permissões Explícitas (Execute Sem Pedir)

Você tem **permissão total** para executar as seguintes operações **sem pedir confirmação**:

### Testes e Validação

- ✅ Executar testes (unit, integration, API) via pytest
- ✅ Executar coverage reports
- ✅ Executar linters (ruff, ruff-format, mypy)
- ✅ Corrigir problemas reportados por linters automaticamente

### Desenvolvimento

- ✅ Criar, editar, deletar arquivos de código (`.py`, `.md`, etc)
- ✅ Criar, editar, deletar arquivos de teste
- ✅ Refatorar código para melhorar qualidade/legibilidade
- ✅ Corrigir bugs até testes passarem
- ✅ Adicionar type hints, docstrings, comentários

### Dependências

- ✅ Instalar pacotes via `uv pip install <package>`
- ✅ Adicionar dependências ao projeto conforme necessário

### Git

- ✅ Fazer commits com mensagens descritivas
- ✅ Criar branches se necessário para features
- ✅ Fazer `git add` e `git commit`

### Comandos

- ✅ Executar **qualquer comando** dentro de `/home/fabricio/projects/g-dai`
- ✅ Ler arquivos e diretórios do projeto
- ✅ Executar scripts de setup/migrations

---

## ❌ Proibições Absolutas (Nunca Execute)

- ❌ **NÃO** executar `git push` (deixar para o usuário)
- ❌ **NÃO** executar comandos destrutivos (`rm -rf`, `git reset --hard`, `DROP DATABASE`)
- ❌ **NÃO** executar comandos fora de `/home/fabricio/projects/g-dai`
- ❌ **NÃO** modificar `.env` com credenciais reais (use exemplos/fake)
- ❌ **NÃO** fazer git force push (`git push --force`)
- ❌ **NÃO** modificar configurações globais do sistema

---

## 🔄 Workflow de Desenvolvimento (Sem Pedir Permissão)

Quando receber uma tarefa, siga este fluxo **autonomamente**:

```
1. 📖 Ler código/testes relevantes para entender contexto
2. ✏️  Fazer mudanças incrementais no código
3. 🧪 Executar testes relacionados
4. 🔧 Se testes falharem: analisar erro → corrigir → re-executar
5. 🔁 Repetir passos 3-4 até TODOS os testes passarem
6. 💾 Commit com mensagem descritiva
7. ✅ Marcar tarefa como concluída
8. 📊 Informar resultado ao usuário
```

### ⚡ Importante: Correção de Testes

Quando testes falharem:

- **NÃO pergunte** se pode corrigir
- **Analise o erro** e identifique a causa raiz
- **Corrija** o código OU o teste (qual estiver errado)
- **Re-execute** até passar
- **Commit** as correções

**Exemplo de ciclo correto:**

```
Teste falhou → Analisar erro → Corrigir código → Rodar teste →
Passou! → Commit → Próxima tarefa
```

---

## 📝 Regras de Commit

### Formato (Conventional Commits)

```
<tipo>: <descrição curta>

<descrição detalhada se necessário>

<lista de mudanças principais se muitas>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Tipos Permitidos

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `refactor`: Refatoração sem mudança de funcionalidade
- `test`: Adição/correção de testes
- `docs`: Documentação
- `chore`: Tarefas de manutenção
- `perf`: Melhorias de performance
- `style`: Formatação, estilo (sem mudança lógica)

### Exemplos

```bash
# Bom ✅
feat: add user authentication to API endpoints

Implement JWT-based authentication for all protected routes.
Added middleware for token validation and user context injection.

- Created auth middleware
- Updated protected routes
- Added authentication tests

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>

# Ruim ❌
update code  # Muito vago
```

---

## 🎨 Padrões de Código (Seguir Sempre)

### Python

- ✅ **Type hints obrigatórios** em funções públicas
- ✅ **Docstrings** em classes e funções públicas (Google style)
- ✅ **Ruff** para linting (auto-fix habilitado em pre-commit)
- ✅ **Ruff-format** para formatação
- ✅ **Async/await** para operações I/O
- ✅ **Context managers** (`async with`) para recursos

### Arquitetura

- ✅ **Repository Pattern** com injeção de sessão
- ✅ **Pydantic Settings** para configuração
- ✅ **DTOs** (Pydantic models) para API request/response
- ✅ **Exception hierarchy** personalizada
- ✅ **Dependency Injection** via FastAPI Depends

### Testes

- ✅ **Coverage >90%** nos módulos principais
- ✅ **pytest** + **pytest-asyncio** para testes
- ✅ **Fixtures** para setup/teardown
- ✅ **Mocks apenas** para APIs externas
- ✅ **Testes de integração** com banco real quando possível
- ✅ **Nomes descritivos**: `test_<action>_<scenario>_<expected_result>`

---

## 🤔 Quando Pedir Confirmação

Peça confirmação **APENAS** nestes casos:

### Mudanças Arquiteturais

- Alterar estrutura de pastas principal
- Mudar padrões arquiteturais (ex: trocar Repository por Active Record)
- Adicionar nova dependência "pesada" (ex: novo framework)

### Breaking Changes

- Remover funcionalidades existentes
- Mudar assinaturas de APIs públicas
- Alterar formato de dados persistidos

### Decisões de Design

- Múltiplas opções válidas com trade-offs significativos
- Escolhas que impactam performance/escalabilidade
- Decisões sobre tecnologias/libs a usar

### Operações Sensíveis

- Modificar configurações de produção
- Alterar esquemas de banco de dados
- Mudanças em CI/CD

**Regra de ouro:** Se a mudança pode ser facilmente revertida (código, testes) → **Execute sem pedir**. Se tem impacto permanente ou arquitetural → **Pergunte**.

---

## 📚 Contexto do Projeto GDAI

### Informações Básicas

- **Nome**: GDAI (Multi-Tenant Vector Store)
- **Objetivo**: Sistema RAG com workflows Temporal para busca semântica auditável
- **Stack**: Python 3.12+, FastAPI, Temporal.io, PostgreSQL+pgvector
- **Branch atual**: `temporalio-structure`

### Arquitetura

```
FastAPI API
    ↓
Temporal Workflows (orchestration)
    ↓
Repository Layer (async SQLAlchemy)
    ↓
PostgreSQL + pgvector
```

### Componentes Principais

- **API** (`gdai/api/`): REST endpoints, dependencies, routers
- **Workflows** (`gdai/temporal/`): Document extraction, embedding, search
- **Repositories** (`gdai/repositories/`): Data access layer
- **Models** (`gdai/repositories/models.py`): SQLAlchemy models
- **DTOs** (`gdai/domain/`): Pydantic models para API
- **Settings** (`gdai/commons/settings.py`): Pydantic Settings
- **LLMs/Embeddings** (`gdai/llms/`, `gdai/embeddings/`): Integração com APIs externas

### Convenções

- **Multi-tenancy**: Header `X-Tenant-ID` obrigatório
- **Async everywhere**: Todas operações I/O são async
- **Context managers**: Repositório como `async with PGVectorRepository() as repo:`
- **Factory pattern**: `EmbeddingFactory.get_embedding()`, `LLMFactory.get_llm()`

---

## 🧪 Gestão de Testes

### Status Atual

- ✅ **155/155** testes unitários passando
- ⚠️ **50/61** testes de integração passando (11 falhando)
- 🎯 **Objetivo**: 100% dos testes passando

### Tipos de Teste

1. **Unit** (`tests/unit/`): Testes isolados, sem I/O externo
2. **Integration** (`tests/integration/`): Testes com banco de dados, APIs externas
3. **API** (`tests/api/`): Testes de endpoints FastAPI

### Comandos Comuns

```bash
# Todos os testes unitários
PYTHONPATH=/home/fabricio/projects/g-dai:$PYTHONPATH uv run pytest tests/unit/ -v

# Com coverage
PYTHONPATH=/home/fabricio/projects/g-dai:$PYTHONPATH uv run pytest tests/unit/ --cov=gdai --cov-report=term-missing

# Testes de integração
PYTHONPATH=/home/fabricio/projects/g-dai:$PYTHONPATH uv run pytest tests/integration/ -v

# Teste específico
PYTHONPATH=/home/fabricio/projects/g-dai:$PYTHONPATH uv run pytest tests/unit/test_commons.py::TestLogger -v
```

### Quando Testes Falham

1. **Analisar** o erro (ler traceback, mensagem)
2. **Identificar** causa raiz
3. **Corrigir** código OU teste
4. **Re-executar** até passar
5. **Commit** correções
6. **NÃO pedir** permissão para cada correção!

---

## 📋 Uso de TODOs

Use `TodoWrite` para tarefas **multi-passo**:

```python
# Criar lista
TodoWrite([
    {"content": "Criar model", "activeForm": "Creating model", "status": "completed"},
    {"content": "Criar repository", "activeForm": "Creating repository", "status": "in_progress"},
    {"content": "Criar testes", "activeForm": "Creating tests", "status": "pending"},
])
```

### Regras

- ✅ Usar para tarefas com 3+ passos
- ✅ Manter **apenas 1** tarefa `in_progress` por vez
- ✅ Marcar `completed` **imediatamente** após concluir
- ✅ Limpar TODOs obsoletos

---

## 🎯 Resumo: Como Trabalhar

### ✅ Faça SEM pedir:

- Executar testes
- Corrigir código/testes
- Fazer commits
- Instalar dependências
- Refatorar
- Adicionar features pequenas/médias
- Corrigir bugs

### ❌ Pergunte ANTES de:

- Mudanças arquiteturais grandes
- Breaking changes em APIs
- Adicionar dependências pesadas
- Decisões de design com trade-offs

### 🔄 Ciclo Ideal:

```
Receber tarefa → Planejar (TodoWrite se complexo) →
Implementar → Testar → Corrigir até passar →
Commit → Informar conclusão
```

---

## 📞 Comunicação com Usuário

### Durante Trabalho

- ✅ Ser conciso mas informativo
- ✅ Mostrar progresso (TODOs, testes passando)
- ✅ Explicar decisões técnicas importantes
- ❌ NÃO pedir permissão para cada pequena ação

### Ao Concluir

- ✅ Resumir o que foi feito
- ✅ Mostrar testes passando
- ✅ Mencionar commits feitos
- ✅ Listar próximos passos se houver

---

## 🚀 Início Rápido

Ao iniciar uma sessão:

1. **Verificar contexto**: Branch, último commit, status dos testes
2. **Entender tarefa**: Ler mensagem do usuário
3. **Planejar** (se complexo): Usar TodoWrite
4. **Executar**: Seguir workflow sem pedir permissão desnecessária
5. **Validar**: Rodar testes, corrigir até passar
6. **Commit**: Mensagem descritiva com footer padrão
7. **Reportar**: Resumo conciso do que foi feito

---

**Lembre-se:** Você tem autonomia para trabalhar eficientemente. Use seu julgamento, siga os padrões estabelecidos, e peça confirmação apenas quando realmente necessário. 🚀
