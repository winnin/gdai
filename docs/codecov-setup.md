# Configuração do Codecov

Este guia explica como configurar o Codecov para exibir o badge de coverage no README.

## O que é Codecov?

Codecov é um serviço gratuito (para projetos open source) que rastreia a cobertura de código dos seus testes e exibe badges e relatórios detalhados.

## Passo a Passo

### 1. Criar conta no Codecov

1. Acesse [codecov.io](https://codecov.io)
2. Clique em "Sign up" e escolha "Sign up with GitHub"
3. Autorize o Codecov a acessar suas repositórios

### 2. Adicionar o repositório

1. No dashboard do Codecov, clique em "Add new repository"
2. Procure por `winnin/gdai` na lista
3. Clique em "Setup repo"

### 3. Obter o token (se repositório privado)

**Para repositórios públicos**: O token não é necessário! O badge funcionará automaticamente.

**Para repositórios privados**:

1. No Codecov, vá em Settings do repositório
2. Copie o "Upload token"
3. No GitHub, vá em Settings → Secrets and variables → Actions
4. Clique em "New repository secret"
5. Nome: `CODECOV_TOKEN`
6. Valor: Cole o token copiado
7. Clique em "Add secret"

### 4. Fazer o primeiro push

Depois de configurar:

```bash
git add .github/workflows/tests.yml
git commit -m "ci: enable code coverage reporting"
git push
```

O GitHub Actions vai executar, gerar o coverage e enviar para o Codecov.

### 5. Verificar o badge

Após o primeiro upload bem-sucedido:

1. Vá para https://codecov.io/gh/winnin/gdai
2. O badge deve aparecer no topo da página
3. No README.md, o badge já está configurado:
   ```markdown
   [![codecov](https://codecov.io/gh/winnin/gdai/branch/main/graph/badge.svg)](https://codecov.io/gh/winnin/gdai)
   ```

## Alternativa: Badge Local (sem Codecov)

Se você **não quiser usar Codecov**, pode usar um badge estático ou gerar localmente:

### Opção 1: Badge Shields.io (Dinâmico via GitHub Actions)

Adicione ao README.md:

```markdown
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)
```

Você precisa atualizar manualmente o valor após cada release.

### Opção 2: Badge via Artifact

1. Gere um badge JSON no workflow:

```yaml
- name: Generate coverage badge
  run: |
    coverage=$(uv run pytest tests/unit/ --cov=gdai --cov-report=term | grep TOTAL | awk '{print $4}')
    echo "{\"schemaVersion\":1,\"label\":\"coverage\",\"message\":\"$coverage\",\"color\":\"green\"}" > coverage-badge.json

- name: Upload badge
  uses: actions/upload-artifact@v4
  with:
    name: coverage-badge
    path: coverage-badge.json
```

2. Use o GitHub Pages para hospedar o badge.

### Opção 3: Badge via Gist

Use o [coverage-badge](https://github.com/dbrgn/coverage-badge) para gerar e atualizar automaticamente.

## Verificando o Coverage Localmente

```bash
# Executar testes com coverage
./gdai/scripts/tests.sh unit

# Abrir relatório HTML
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Troubleshooting

### Badge não aparece

1. Verifique se o workflow executou: https://github.com/winnin/gdai/actions
2. Verifique se o upload para Codecov foi bem-sucedido nos logs
3. Aguarde alguns minutos - o Codecov pode demorar para processar
4. Limpe o cache do navegador

### Badge mostra "unknown"

1. O primeiro upload ainda não foi processado
2. O branch no badge (`main`) precisa corresponder ao branch padrão
3. Verifique se o coverage.xml foi gerado corretamente

### Erro "CODECOV_TOKEN not found"

**Para repositórios públicos**: Remova a linha `token: ${{ secrets.CODECOV_TOKEN }}` do workflow.

**Para repositórios privados**: Configure o secret conforme o passo 3.

## URLs Úteis

- **Dashboard Codecov**: https://codecov.io/gh/winnin/gdai
- **Badge URL**: https://codecov.io/gh/winnin/gdai/branch/main/graph/badge.svg
- **Documentação**: https://docs.codecov.com/docs

## Configuração Avançada (Opcional)

Crie um arquivo `.codecov.yml` na raiz do projeto para customizar:

```yaml
coverage:
  status:
    project:
      default:
        target: 80% # Meta de coverage
        threshold: 5% # Tolerância
    patch:
      default:
        target: 80%

ignore:
  - "tests/"
  - "**/__init__.py"

comment:
  behavior: default
  require_changes: false
```

---

**Pronto!** Agora seu badge de coverage deve funcionar no GitHub. 🎉
