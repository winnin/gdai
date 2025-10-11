# GitHub Actions - Workflows do GDAI

Este documento explica todos os workflows de CI/CD configurados no projeto GDAI.

## 📊 Visão Geral dos Workflows

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GitHub Repository                            │
│                         (winnin/gdai)                               │
└────────────────────┬────────────────────────────────────────────────┘
                     │
                     │ git push / pull request
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      GitHub Actions Triggers                         │
├─────────────────┬───────────────────┬───────────────────────────────┤
│                 │                   │                               │
│   on: push      │  on: pull_request │   on: schedule / manual      │
│                 │                   │                               │
└────────┬────────┴────────┬──────────┴───────────┬───────────────────┘
         │                 │                      │
         ▼                 ▼                      ▼
    ┌────────┐      ┌──────────┐         ┌──────────────┐
    │ Tests  │      │Pre-commit│         │  GH Pages    │
    │Workflow│      │ Workflow │         │   Workflow   │
    └────────┘      └──────────┘         └──────────────┘
```

## 🔬 Workflow 1: Tests (tests.yml)

### Diagrama de Execução

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Tests Workflow                                │
│                    (.github/workflows/tests.yml)                     │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                │ Trigger: push / pull_request
                                ▼
                    ┌───────────────────────┐
                    │  Setup Environment    │
                    ├───────────────────────┤
                    │ • Checkout code       │
                    │ • Setup Python 3.12   │
                    │ • Install UV          │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Start Services       │
                    ├───────────────────────┤
                    │ PostgreSQL Container  │
                    │ • Image: pgvector     │
                    │ • Port: 5555          │
                    │ • Health checks       │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Install Dependencies  │
                    ├───────────────────────┤
                    │ • uv sync --all-groups│
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Create .env File     │
                    ├───────────────────────┤
                    │ EMBEDDING_API_KEY=... │
                    │ EMBEDDING_MODEL=...   │
                    │ LLM_API_KEY=...       │
                    │ PGVECTOR_*=...        │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │   Run Unit Tests      │
                    ├───────────────────────┤
                    │ pytest tests/unit/    │
                    │ --cov=gdai            │
                    │ --cov-report=xml      │
                    │ --cov-report=html     │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Upload to Codecov    │
                    ├───────────────────────┤
                    │ • Send coverage.xml   │
                    │ • Generate badge      │
                    │ • Update dashboard    │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Archive Artifacts    │
                    ├───────────────────────┤
                    │ • HTML report         │
                    │ • Retention: 14 days  │
                    └───────────┬───────────┘
                                │
                                ▼
                         ┌──────────┐
                         │ Success! │
                         └──────────┘
```

### Configuração Detalhada

```yaml
name: Tests

on:
  push: # Executa em todo push
  pull_request: # Executa em PRs

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres: # PostgreSQL container para testes
        image: ankane/pgvector:latest
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpwd
          POSTGRES_DB: vectordb
        ports:
          - 5555:5432
```

### Como Funciona:

1. **Trigger**: Executa automaticamente em:

   - Todo `git push` para qualquer branch
   - Toda abertura/atualização de Pull Request

2. **Setup**:

   - Faz checkout do código
   - Configura Python 3.12
   - Instala UV (gerenciador de pacotes)

3. **Services**:

   - Inicia PostgreSQL com pgvector em container Docker
   - Aguarda health check antes de prosseguir
   - Disponível em `localhost:5555`

4. **Dependências**:

   - Executa `uv sync --all-groups`
   - Instala todas as dependências do projeto

5. **Environment**:

   - Cria arquivo `.env` dinamicamente
   - Define variáveis necessárias para testes
   - Usa valores mock para API keys

6. **Testes**:

   - Executa testes unitários em `tests/unit/`
   - Gera relatório de coverage em XML e HTML
   - Falha se coverage for muito baixo

7. **Coverage**:

   - Envia `coverage.xml` para Codecov
   - Codecov processa e atualiza badge
   - Disponível em https://codecov.io/gh/winnin/gdai

8. **Artifacts**:
   - Salva relatório HTML como artifact
   - Disponível para download por 14 dias
   - Acessível na aba "Actions" do GitHub

### Visualizando Resultados:

```
GitHub Repository
    │
    └─> Actions Tab
            │
            └─> Workflow: "Tests"
                    │
                    ├─> ✓ Build logs
                    ├─> ✓ Test results
                    ├─> 📊 Coverage report (artifact)
                    └─> 🔗 Codecov link
```

## ✨ Workflow 2: Pre-commit (pre-commit.yml)

### Diagrama de Execução

```
┌──────────────────────────────────────────────────────────────────────┐
│                      Pre-commit Workflow                              │
│                  (.github/workflows/pre-commit.yml)                  │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                │ Trigger: push / pull_request
                                ▼
                    ┌───────────────────────┐
                    │  Setup Environment    │
                    ├───────────────────────┤
                    │ • Checkout code       │
                    │ • Setup Python 3.11   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Run Pre-commit Hooks  │
                    ├───────────────────────┤
                    │ • ruff (linting)      │
                    │ • ruff-format         │
                    │ • check-json          │
                    │ • fix-end-of-files    │
                    │ • trim-trailing-ws    │
                    │ • prettier (markdown) │
                    └───────────┬───────────┘
                                │
                                ▼
                         ┌──────────┐
                         │  Result  │
                         ├──────────┤
                         │ ✓ Pass   │
                         │ ✗ Fail   │
                         └──────────┘
```

### Hooks Executados:

```
┌──────────────────┐
│  Code Quality    │
├──────────────────┤
│                  │
│  1. ruff         │──> Linting Python (PEP 8, imports, etc)
│     └─ check     │
│                  │
│  2. ruff-format  │──> Formatação de código Python
│     └─ format    │
│                  │
├──────────────────┤
│  File Checks     │
├──────────────────┤
│                  │
│  3. check-json   │──> Valida arquivos JSON
│                  │
│  4. end-of-files │──> Garante newline no final
│                  │
│  5. trim-ws      │──> Remove espaços em branco no final
│                  │
│  6. prettier     │──> Formata Markdown, YAML, JSON
│                  │
└──────────────────┘
```

### Como Funciona:

1. **Trigger**: Executa em:

   - Todo push
   - Todo pull request

2. **Validações**:

   - Código Python segue PEP 8
   - Imports organizados
   - Formatação consistente
   - Arquivos JSON válidos
   - Markdown bem formatado

3. **Resultado**:
   - ✅ Pass: Código está limpo
   - ❌ Fail: Precisa correções

## 📄 Workflow 3: GitHub Pages (gh-pages.yml)

### Diagrama de Execução

```
┌──────────────────────────────────────────────────────────────────────┐
│                      GH Pages Workflow                                │
│                  (.github/workflows/gh-pages.yml)                    │
└──────────────────────────────────────────────────────────────────────┘
                                │
                                │ Trigger: push to main OR manual
                                ▼
                    ┌───────────────────────┐
                    │  Build Documentation  │
                    ├───────────────────────┤
                    │ • Generate docs       │
                    │ • Build static site   │
                    └───────────┬───────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │  Deploy to GH Pages   │
                    ├───────────────────────┤
                    │ • Push to gh-pages    │
                    │ • Update site         │
                    └───────────┬───────────┘
                                │
                                ▼
                         ┌──────────┐
                         │ Published│
                         └──────────┘
                    https://winnin.github.io/gdai
```

## 🔄 Fluxo Completo de Desenvolvimento

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Developer Workflow                                │
└─────────────────────────────────────────────────────────────────────┘

Developer
    │
    │ 1. Escreve código
    │
    ├─> git add .
    ├─> git commit
    │       │
    │       └─> Local pre-commit hooks executam
    │           ├─> ruff
    │           ├─> ruff-format
    │           ├─> prettier
    │           └─> outros checks
    │
    ├─> git push origin feature-branch
    │
    ▼
GitHub
    │
    ├─────────────────────────────────────────┐
    │                                         │
    ▼                                         ▼
┌────────────┐                        ┌──────────────┐
│   Tests    │                        │  Pre-commit  │
│  Workflow  │                        │   Workflow   │
└─────┬──────┘                        └──────┬───────┘
      │                                      │
      ├─> Setup Environment                 ├─> Run Hooks
      ├─> Start PostgreSQL                  ├─> Validate Code
      ├─> Run Tests                         └─> Report ✓/✗
      ├─> Generate Coverage
      ├─> Upload to Codecov
      └─> Archive Report
      │
      ▼
   ✓ All Checks Pass
      │
      ▼
Create Pull Request
      │
      ├─> Tests badge: ✓ passing
      ├─> Pre-commit badge: ✓ passing
      ├─> Coverage badge: 85%
      │
      ▼
Code Review
      │
      ▼
Merge to Main
      │
      ├─> All workflows re-run
      ├─> GH Pages updates
      └─> Deploy (if configured)
```

## 📊 Badges Disponíveis

```
README.md
    │
    ├─> [![Tests](...)         ]  ─┬─> GitHub Actions: tests.yml
    │                               └─> Status: passing/failing
    │
    ├─> [![Pre-commit](...)]    ─┬─> GitHub Actions: pre-commit.yml
    │                             └─> Status: passing/failing
    │
    └─> [![codecov](...)]       ─┬─> Codecov.io
                                  └─> Coverage: 85%
```

### URLs dos Badges:

```markdown
<!-- Tests -->

https://github.com/winnin/gdai/actions/workflows/tests.yml/badge.svg

<!-- Pre-commit -->

https://github.com/winnin/gdai/actions/workflows/pre-commit.yml/badge.svg

<!-- Coverage -->

https://codecov.io/gh/winnin/gdai/branch/main/graph/badge.svg
```

## 🛠️ Comandos Úteis

### Executar Localmente (antes do push):

```bash
# Executar pre-commit em todos os arquivos
pre-commit run --all-files

# Executar apenas ruff
pre-commit run ruff --all-files

# Executar testes como no CI
./gdai/scripts/tests.sh unit
```

### Ver Logs do GitHub Actions:

```bash
# Instalar GitHub CLI
gh workflow list

# Ver runs recentes
gh run list

# Ver logs de um run específico
gh run view <run-id> --log
```

### Fazer Download de Artifacts:

```bash
# Via GitHub CLI
gh run download <run-id>

# Via Web
# GitHub → Actions → Workflow Run → Artifacts
```

## 🔐 Secrets Necessários

```
GitHub Repository Settings
    │
    └─> Settings
          │
          └─> Secrets and variables
                │
                └─> Actions
                      │
                      └─> Repository secrets
                            │
                            └─> CODECOV_TOKEN (se repo privado)
```

### Como Adicionar:

1. Acesse Settings → Secrets and variables → Actions
2. Clique "New repository secret"
3. Nome: `CODECOV_TOKEN`
4. Valor: Token do Codecov
5. Save

## 📈 Monitoramento

### GitHub Actions Dashboard:

```
https://github.com/winnin/gdai/actions

┌─────────────────────────────────────────┐
│          Workflow Runs                  │
├─────────────────────────────────────────┤
│ ✓ Tests             #123  main  2m 30s │
│ ✓ Pre-commit        #123  main  45s    │
│ ✓ GH Pages          #122  main  1m 15s │
│ ✗ Tests             #121  feat  Failed │
└─────────────────────────────────────────┘
```

### Codecov Dashboard:

```
https://codecov.io/gh/winnin/gdai

┌─────────────────────────────────────────┐
│          Coverage Report                │
├─────────────────────────────────────────┤
│ Total Coverage:        85.5%            │
│ Files:                 42               │
│ Lines:                 2,534            │
│ Covered:               2,167            │
│                                         │
│ Coverage by Module:                     │
│ • gdai/api/           92%               │
│ • gdai/temporal/      88%               │
│ • gdai/repositories/  81%               │
└─────────────────────────────────────────┘
```

## 🚨 Troubleshooting

### Workflow falha com "Database connection error"

```
Causa: PostgreSQL service não iniciou corretamente

Solução:
1. Verificar health check no workflow
2. Aumentar timeout do health check
3. Verificar portas disponíveis
```

### Coverage não é enviado ao Codecov

```
Causa: Token não configurado ou coverage.xml não gerado

Solução:
1. Verificar se CODECOV_TOKEN está configurado
2. Verificar logs: "Upload coverage to Codecov"
3. Confirmar que coverage.xml existe
```

### Pre-commit falha mas código está correto

```
Causa: Hooks desatualizados

Solução:
1. pre-commit autoupdate
2. pre-commit run --all-files
3. git add .
4. git commit --amend
```

## 📚 Referências

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Codecov Documentation](https://docs.codecov.com)
- [Pre-commit Documentation](https://pre-commit.com)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io)

---

**Última atualização**: 2025-10-11
