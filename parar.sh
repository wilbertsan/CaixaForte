#!/bin/bash
# ==============================================
#   CAIXA FORTE - Parar todos os processos
# ==============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/caixa_forte.pid"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ ! -f "$PID_FILE" ]; then
    echo -e "${YELLOW}Nenhum processo Caixa Forte registrado.${NC}"
    exit 0
fi

echo "Parando processos Caixa Forte..."
while read -r pid; do
    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null
        echo -e "  PID $pid ${RED}encerrado${NC}"
    else
        echo -e "  PID $pid (já não estava rodando)"
    fi
done < "$PID_FILE"

rm -f "$PID_FILE"
echo -e "${GREEN}Tudo encerrado.${NC}"
