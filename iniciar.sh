#!/bin/bash
# ==============================================
#   CAIXA FORTE - Inicializador Linux
#   Telegram Bot + Agendador Professor Pardal
#   Processos persistem após encerrar SSH
# ==============================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

TELEGRAM_LOG="$LOG_DIR/telegram_bot.log"
SCHEDULER_LOG="$LOG_DIR/scheduler.log"
PID_FILE="$LOG_DIR/caixa_forte.pid"

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Descobrir caminho do python dentro do venv
if [ -f "$SCRIPT_DIR/venv/bin/python" ]; then
    PYTHON="$SCRIPT_DIR/venv/bin/python"
elif [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    PYTHON="$SCRIPT_DIR/.venv/bin/python"
else
    echo -e "${RED}Erro: ambiente virtual não encontrado (venv/ ou .venv/)${NC}"
    echo "Crie com: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verificar .env
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    echo -e "${RED}Erro: arquivo .env não encontrado${NC}"
    echo "Copie .env.example para .env e preencha as chaves."
    exit 1
fi

# Parar processos anteriores
if [ -f "$PID_FILE" ]; then
    echo -e "${YELLOW}Parando processos anteriores...${NC}"
    while read -r pid; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            echo "  PID $pid encerrado"
        fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    sleep 1
fi

echo "=================================================="
echo "  CAIXA FORTE - Sistema Financeiro DuckTales"
echo "  Modo: nohup (sobrevive ao encerrar SSH)"
echo "=================================================="
echo ""

# Iniciar Scheduler com nohup
echo -e "${GREEN}[1/2] Iniciando Agendador (Professor Pardal - 10:00 diário)...${NC}"
nohup "$PYTHON" "$SCRIPT_DIR/scheduler.py" >> "$SCHEDULER_LOG" 2>&1 &
SCHEDULER_PID=$!
disown "$SCHEDULER_PID"
echo "$SCHEDULER_PID" > "$PID_FILE"

sleep 1
if kill -0 "$SCHEDULER_PID" 2>/dev/null; then
    echo -e "      ${GREEN}OK${NC} | PID: $SCHEDULER_PID"
else
    echo -e "      ${RED}FALHOU${NC} | Verifique: $SCHEDULER_LOG"
    exit 1
fi

# Iniciar Telegram Bot com nohup
echo -e "${GREEN}[2/2] Iniciando Telegram Bot...${NC}"
nohup "$PYTHON" "$SCRIPT_DIR/telegram_bot.py" >> "$TELEGRAM_LOG" 2>&1 &
TELEGRAM_PID=$!
disown "$TELEGRAM_PID"
echo "$TELEGRAM_PID" >> "$PID_FILE"

sleep 2
if kill -0 "$TELEGRAM_PID" 2>/dev/null; then
    echo -e "      ${GREEN}OK${NC} | PID: $TELEGRAM_PID"
else
    echo -e "      ${RED}FALHOU${NC} | Verifique: $TELEGRAM_LOG"
    kill "$SCHEDULER_PID" 2>/dev/null || true
    rm -f "$PID_FILE"
    exit 1
fi

echo ""
echo "=================================================="
echo -e "  ${GREEN}Tudo rodando em background!${NC}"
echo ""
echo "  Scheduler PID: $SCHEDULER_PID"
echo "  Telegram  PID: $TELEGRAM_PID"
echo "  PIDs salvos:   $PID_FILE"
echo ""
echo "  Logs:"
echo "    tail -f $SCHEDULER_LOG"
echo "    tail -f $TELEGRAM_LOG"
echo ""
echo "  Parar tudo:  ./parar.sh"
echo "  Status:      ./status.sh"
echo ""
echo "  Pode fechar o SSH. Os processos continuam."
echo "=================================================="
