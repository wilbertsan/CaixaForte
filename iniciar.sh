#!/bin/bash
# ==============================================
#   CAIXA FORTE - Inicializador Linux
#   Telegram Bot + Agendador Professor Pardal
# ==============================================

set -e

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

# Ativar venv
if [ -d "venv/bin" ]; then
    source venv/bin/activate
elif [ -d ".venv/bin" ]; then
    source .venv/bin/activate
else
    echo -e "${RED}Erro: ambiente virtual não encontrado (venv/ ou .venv/)${NC}"
    echo "Crie com: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verificar .env
if [ ! -f ".env" ]; then
    echo -e "${RED}Erro: arquivo .env não encontrado${NC}"
    echo "Copie .env.example para .env e preencha as chaves."
    exit 1
fi

# Função para parar processos anteriores
parar_processos() {
    if [ -f "$PID_FILE" ]; then
        echo -e "${YELLOW}Parando processos anteriores...${NC}"
        while read -r pid; do
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi
}

# Função de limpeza ao sair
cleanup() {
    echo ""
    echo -e "${YELLOW}Encerrando Caixa Forte...${NC}"
    parar_processos
    echo -e "${GREEN}Encerrado.${NC}"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Parar instâncias anteriores
parar_processos

echo "=================================================="
echo "  CAIXA FORTE - Sistema Financeiro DuckTales"
echo "=================================================="
echo ""

# Iniciar Scheduler (Professor Pardal - diário 10:00)
echo -e "${GREEN}[1/2] Iniciando Agendador (Professor Pardal - 10:00 diário)...${NC}"
python scheduler.py >> "$SCHEDULER_LOG" 2>&1 &
SCHEDULER_PID=$!
echo "$SCHEDULER_PID" > "$PID_FILE"
echo "      PID: $SCHEDULER_PID | Log: $SCHEDULER_LOG"

# Verificar se scheduler iniciou
sleep 1
if ! kill -0 "$SCHEDULER_PID" 2>/dev/null; then
    echo -e "${RED}      Erro: Agendador não iniciou. Verifique $SCHEDULER_LOG${NC}"
    exit 1
fi

# Iniciar Telegram Bot
echo -e "${GREEN}[2/2] Iniciando Telegram Bot...${NC}"
python telegram_bot.py >> "$TELEGRAM_LOG" 2>&1 &
TELEGRAM_PID=$!
echo "$TELEGRAM_PID" >> "$PID_FILE"
echo "      PID: $TELEGRAM_PID | Log: $TELEGRAM_LOG"

# Verificar se bot iniciou
sleep 2
if ! kill -0 "$TELEGRAM_PID" 2>/dev/null; then
    echo -e "${RED}      Erro: Telegram Bot não iniciou. Verifique $TELEGRAM_LOG${NC}"
    kill "$SCHEDULER_PID" 2>/dev/null || true
    exit 1
fi

echo ""
echo "=================================================="
echo -e "  ${GREEN}Tudo rodando!${NC}"
echo "  Scheduler PID: $SCHEDULER_PID"
echo "  Telegram  PID: $TELEGRAM_PID"
echo ""
echo "  Logs em: $LOG_DIR/"
echo "  Acompanhar: tail -f $LOG_DIR/*.log"
echo ""
echo "  Pressione Ctrl+C para encerrar tudo"
echo "=================================================="
echo ""

# Aguardar — se qualquer processo morrer, avisa
while true; do
    if ! kill -0 "$SCHEDULER_PID" 2>/dev/null; then
        echo -e "${RED}[ALERTA] Agendador parou inesperadamente. Reiniciando...${NC}"
        python scheduler.py >> "$SCHEDULER_LOG" 2>&1 &
        SCHEDULER_PID=$!
        echo "$SCHEDULER_PID" > "$PID_FILE"
        echo "$TELEGRAM_PID" >> "$PID_FILE"
        echo -e "${GREEN}         Reiniciado com PID: $SCHEDULER_PID${NC}"
    fi

    if ! kill -0 "$TELEGRAM_PID" 2>/dev/null; then
        echo -e "${RED}[ALERTA] Telegram Bot parou inesperadamente. Reiniciando...${NC}"
        python telegram_bot.py >> "$TELEGRAM_LOG" 2>&1 &
        TELEGRAM_PID=$!
        # Reescrever PID file
        echo "$SCHEDULER_PID" > "$PID_FILE"
        echo "$TELEGRAM_PID" >> "$PID_FILE"
        echo -e "${GREEN}         Reiniciado com PID: $TELEGRAM_PID${NC}"
    fi

    sleep 10
done
