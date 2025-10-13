#!/bin/bash
# Script para atualizar documentação do MkDocs
# Usage: ./gdai/scripts/update_docs.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "📚 Atualizando documentação do MkDocs..."
echo ""

# Copia arquivos principais para docs/
echo "📝 Copiando README.md para docs/index.md..."
cp README.md docs/index.md

echo "📝 Copiando ROADMAP.md para docs/..."
cp ROADMAP.md docs/

echo "📝 Copiando CHANGELOG.md para docs/..."
cp CHANGELOG.md docs/

# Ajusta links no index.md (remove prefixo docs/)
echo "🔧 Ajustando links em index.md..."
sed -Ei 's#docs/([a-zA-Z0-9_-]+\.md)#\1#g' docs/index.md

echo ""
echo "✅ Documentação atualizada com sucesso!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📖 Próximos passos:"
echo ""
echo "  1. Visualizar localmente:"
echo "     uv run mkdocs serve"
echo "     Acesse: http://localhost:8000"
echo ""
echo "  2. Build estático (opcional):"
echo "     uv run mkdocs build"
echo "     Saída: site/"
echo ""
echo "  3. Deploy para GitHub Pages:"
echo "     uv run mkdocs gh-deploy --force"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
