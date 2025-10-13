# GitHub Configuration Guide

Este documento descreve todas as configurações necessárias no GitHub para que os workflows funcionem corretamente.

## 📋 Índice

- [Secrets Necessários](#secrets-necessários)
- [Branch Protection Rules](#branch-protection-rules)
- [Repository Settings](#repository-settings)
- [GitHub Actions Permissions](#github-actions-permissions)
- [Dependabot Configuration](#dependabot-configuration)
- [CodeQL Setup](#codeql-setup)

---

## 🔐 Secrets Necessários

Configure os seguintes secrets em: **Settings → Secrets and variables → Actions → New repository secret**

### ⚠️ Secrets Recomendados para Testes Completos

**IMPORTANTE**: Sem estes secrets, ~36 testes de integração serão **pulados (skipped)** mas o build **não falhará**.

| Secret Name         | Description                             | How to Get                            | Impacto sem o Secret            |
| ------------------- | --------------------------------------- | ------------------------------------- | ------------------------------- |
| `EMBEDDING_API_KEY` | Cohere API key para testes de embedding | https://dashboard.cohere.com/api-keys | ~18 testes de embedding skipped |
| `LLM_API_KEY`       | OpenAI API key para testes de LLM       | https://platform.openai.com/api-keys  | ~18 testes de LLM skipped       |

**Com API keys**: 139 testes de integração executam
**Sem API keys**: 103 testes de integração executam (36 skipped)

### Optional Secrets

| Secret Name        | Description                             | How to Get                                                 |
| ------------------ | --------------------------------------- | ---------------------------------------------------------- |
| `CODECOV_TOKEN`    | Token for uploading coverage to Codecov | https://codecov.io/ → Sign up → Get token for your repo    |
| `GITLEAKS_LICENSE` | License for Gitleaks (optional)         | Optional - only needed for private repos with Gitleaks Pro |

---

## 🔒 Branch Protection Rules

Configure em: **Settings → Branches → Add branch protection rule**

### Para branch `main`:

1. **Branch name pattern**: `main`

2. **Protect matching branches**:
   - ✅ Require a pull request before merging
     - ✅ Require approvals: **1** (ou mais)
     - ✅ Dismiss stale pull request approvals when new commits are pushed
     - ✅ Require review from Code Owners (if CODEOWNERS file exists)
   - ✅ Require status checks to pass before merging
     - ✅ Require branches to be up to date before merging
     - **Required status checks**:
       - `Code Quality Checks`
       - `Unit Tests`
       - `Integration Tests`
       - `PR Metadata Validation`
       - `Test Coverage Check`
       - `Security Scan`
   - ✅ Require conversation resolution before merging
   - ✅ Require signed commits (optional, but recommended)
   - ✅ Require linear history
   - ✅ Include administrators (recommended)
   - ✅ Restrict who can push to matching branches (optional)
   - ✅ Allow force pushes: **Never**
   - ✅ Allow deletions: **No**

### Para branch `develop`:

1. **Branch name pattern**: `develop`

2. **Protect matching branches**:
   - ✅ Require a pull request before merging
     - ✅ Require approvals: **1**
   - ✅ Require status checks to pass before merging
     - **Required status checks**:
       - `Code Quality Checks`
       - `Unit Tests`
       - `Integration Tests`
   - ✅ Require conversation resolution before merging
   - ✅ Include administrators

---

## ⚙️ Repository Settings

Configure em: **Settings → General**

### Pull Requests

- ✅ Allow squash merging
  - Default message: **Pull request title and description**
- ✅ Allow merge commits (optional)
- ❌ Allow rebase merging (optional)
- ✅ Always suggest updating pull request branches
- ✅ Allow auto-merge
- ✅ Automatically delete head branches

### Features

- ✅ Issues
- ✅ Projects (optional)
- ✅ Discussions (optional)
- ✅ Wiki (optional)

---

## 🤖 GitHub Actions Permissions

Configure em: **Settings → Actions → General**

### Workflow permissions

- ✅ Read and write permissions
- ✅ Allow GitHub Actions to create and approve pull requests

### Fork pull request workflows

- ✅ Require approval for first-time contributors
- ✅ Require approval for all outside collaborators

---

## 📦 Dependabot Configuration

O arquivo `.github/dependabot.yml` já está configurado. Para ativar:

1. Vá em: **Settings → Security → Code security and analysis**
2. Ative:

   - ✅ Dependabot alerts
   - ✅ Dependabot security updates
   - ✅ Grouped security updates

3. **Dependabot version updates** são configurados via arquivo `.github/dependabot.yml`

### Customizações no dependabot.yml

Edite o arquivo para ajustar:

- **reviewers**: Lista de usuários para revisar PRs
- **assignees**: Lista de usuários para atribuir PRs
- **schedule.time**: Horário de execução
- **open-pull-requests-limit**: Limite de PRs abertos simultaneamente

---

## 🔍 CodeQL Setup

Configure em: **Settings → Security → Code security and analysis**

### Ativar CodeQL

1. ✅ Code scanning
2. ✅ CodeQL analysis
3. Configure:
   - Language: **Python**
   - Query suite: **Security and quality**
   - Schedule: **Weekly** (ou conforme necessário)

### Configuração Avançada (opcional)

Crie `.github/codeql/codeql-config.yml`:

```yaml
name: "CodeQL Config"

queries:
  - uses: security-and-quality

paths-ignore:
  - "tests/**"
  - "docs/**"
  - "**/test_*.py"

paths:
  - "gdai/**"
```

---

## 🔔 Notifications

Configure em: **Settings → Notifications** (configuração pessoal)

Recomendações:

- ✅ Notificações de falhas em workflows
- ✅ Notificações de security alerts
- ✅ Notificações de pull requests que você está reviewando

---

## 📊 Codecov Integration

1. Acesse https://codecov.io/
2. Faça login com GitHub
3. Adicione o repositório `gdai`
4. Copie o token gerado
5. Adicione como secret `CODECOV_TOKEN` no GitHub

### Configuração do Codecov (opcional)

Crie `codecov.yml` na raiz:

```yaml
coverage:
  status:
    project:
      default:
        target: 80%
        threshold: 2%
    patch:
      default:
        target: 70%

comment:
  layout: "reach,diff,flags,files,footer"
  behavior: default

ignore:
  - "tests/**"
  - "**/__pycache__/**"
  - "**/test_*.py"
```

---

## 🚨 Security Settings

Configure em: **Settings → Security**

### Security advisories

- ✅ Private vulnerability reporting

### Code security and analysis

- ✅ Dependency graph
- ✅ Dependabot alerts
- ✅ Dependabot security updates
- ✅ Code scanning (CodeQL)
- ✅ Secret scanning
- ✅ Push protection (para evitar commits com secrets)

---

## 📝 Additional Files to Create

### 1. CODEOWNERS (opcional)

Crie `.github/CODEOWNERS`:

```
# Default owners for everything in the repo
*                   @fabricio

# Specific ownership
/gdai/              @fabricio
/tests/             @fabricio @qa-team
/docs/              @fabricio @docs-team
*.md                @fabricio @docs-team
/.github/           @fabricio @devops-team
```

### 2. Pull Request Template

Crie `.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
## Description

<!-- Describe your changes in detail -->

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Related Issues

<!-- Link related issues here -->

Closes #(issue)

## Screenshots (if applicable)

<!-- Add screenshots here -->

## Additional Notes

<!-- Any additional information -->
```

### 3. Issue Templates

Crie `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug Report
about: Create a report to help us improve
title: "[BUG] "
labels: bug
assignees: ""
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**

- OS: [e.g. Ubuntu 22.04]
- Python Version: [e.g. 3.12]
- GDAI Version: [e.g. 1.0.0]

**Additional context**
Add any other context about the problem here.
```

Crie `.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature Request
about: Suggest an idea for this project
title: "[FEATURE] "
labels: enhancement
assignees: ""
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is.

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear description of any alternative solutions or features you've considered.

**Additional context**
Add any other context or screenshots about the feature request here.
```

---

## ✅ Verification Checklist

Após configurar tudo, verifique:

- [ ] Todos os secrets estão configurados
- [ ] Branch protection rules estão ativas
- [ ] GitHub Actions tem permissões corretas
- [ ] Dependabot está ativo
- [ ] CodeQL está configurado
- [ ] Codecov está integrado
- [ ] Notificações estão configuradas
- [ ] CODEOWNERS está criado (opcional)
- [ ] Templates de PR e Issues estão criados

---

## 🚀 Testing the Setup

Para testar se tudo está funcionando:

1. Crie uma branch: `git checkout -b test/github-actions`
2. Faça uma pequena mudança
3. Push: `git push origin test/github-actions`
4. Crie um PR para `main`
5. Verifique se todos os checks passam
6. Verifique se o coverage report aparece como comentário
7. Verifique se os security scans executam

---

## 📞 Support

Se encontrar problemas:

1. Verifique os logs dos workflows em **Actions**
2. Verifique se todos os secrets estão configurados
3. Verifique as permissões do GitHub Actions
4. Consulte a documentação oficial do GitHub Actions

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Codecov Documentation](https://docs.codecov.com/)
