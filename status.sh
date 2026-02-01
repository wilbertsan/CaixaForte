#!/bin/bash
# ==============================================
#   CAIXA FORTE - Verificar status dos processos
# ==============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/logs/caixa_forte.pid"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo "=================================================="
echo "  CAIXA FORTE - Status"
echo "=================================================="

if [ ! -f "$PID_FILE" ]; then
    echo -e "  ${RED}Nenhum processo registrado.${NC}"
    echo "  Execute: ./iniciar.sh"
    exit 0
fi

PIDS=($(cat "$PID_FILE"))
NOMES=("Scheduler (Prof. Pardal)" "Telegram Bot")

for i in "${!PIDS[@]}"; do
    pid="${PIDS[$i]}"
    nome="${NOMES[$i]:-Processo $i}"
    if kill -0 "$pid" 2>/dev/null; then
        echo -e "  ${GREEN}RODANDO${NC}  $nome (PID: $pid)"
    else
        echo -e "  ${RED}PARADO${NC}   $nome (PID: $pid)"
    fi
done

echo ""
echo "  Logs:"
echo "    tail -f $SCRIPT_DIR/logs/scheduler.log"
echo "    tail -f $SCRIPT_DIR/logs/telegram_bot.log"
echo "=================================================="
