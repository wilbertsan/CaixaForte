#!/bin/bash
# ==============================================
#   CAIXA FORTE - Execução manual avulsa
#   Roda o Professor Pardal uma vez agora
# ==============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON="$SCRIPT_DIR/venv/bin/python"
elif [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
else
    echo "Erro: ambiente virtual não encontrado"
    exit 1
fi

echo "========================================"
echo "  CAIXA FORTE - Execução Manual"
echo "  Processando emails e PDFs agora..."
echo "========================================"
echo ""

"$PYTHON" -c "from scheduler import executar_professor_pardal; executar_professor_pardal()"

echo ""
echo "Execução concluída!"
