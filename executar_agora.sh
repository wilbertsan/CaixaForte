#!/bin/bash
# ==============================================
#   CAIXA FORTE - Execução manual avulsa
#   Roda o Professor Pardal uma vez agora
# ==============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d "venv/bin" ]; then
    source venv/bin/activate
elif [ -d ".venv/bin" ]; then
    source .venv/bin/activate
fi

echo "========================================"
echo "  CAIXA FORTE - Execução Manual"
echo "  Processando emails e PDFs agora..."
echo "========================================"
echo ""

python -c "from scheduler import executar_professor_pardal; executar_professor_pardal()"

echo ""
echo "Execução concluída!"
