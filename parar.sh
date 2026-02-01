#!/bin/bash
# ==============================================
#   CAIXA FORTE - Parar todos os processos
# ==============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/caixa_forte.pid"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ ! -f "$PID_FILE" ]; then
    echo "Nenhum processo Caixa Forte encontrado."
    exit 0
fi

echo -e "${YELLOW}Parando processos Caixa Forte...${NC}"
while read -r pid; do
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null
        echo "  Processo $pid encerrado"
    fi
done < "$PID_FILE"

rm -f "$PID_FILE"
echo -e "${GREEN}Tudo encerrado.${NC}"
