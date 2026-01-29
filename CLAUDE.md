# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Caixa Forte** is a multi-agent financial consulting system built on the Agno framework. It features a DuckTales-themed team of AI agents coordinated by Tio Patinhas (Uncle Scrooge) that provides financial analysis for Brazilian investors including stocks (ações), FIIs (Fundos de Investimento Imobiliário), fixed income (renda fixa), expense tracking, and automated brokerage document processing.

**Language:** All code comments, agent personalities, and user interactions are in Portuguese (Brazilian).

## Commands

```bash
# Run interactive chat interface
python main.py

# Run Telegram bot
python telegram_bot.py

# Run scheduled automation (daily at 10:00 AM)
python scheduler.py

# Windows: one-time automation execution
executar_agora.bat

# Windows: start scheduler daemon
executar_agendador.bat

# Windows (Admin PowerShell): install Windows Task Scheduler
.\instalar_tarefa_windows.ps1
```

## Architecture

### Agent-Tool Pattern

The system uses a delegation-based multi-agent architecture:

```
User Input → Team Coordinator (Tio Patinhas) → Specialist Agent → Tools → External APIs
```

**Agents** (`agents/`): Each agent is an Agno `Agent` with personality, role, instructions, and assigned tools:
- `tio_patinhas.py` - Coordinator, delegates to specialists
- `huguinho.py` - Stock analysis (uses `AcoesTools`)
- `zezinho.py` - FII analysis (uses `FIIsTools`)
- `luizinho.py` - Fixed income (uses `RendaFixaTools`)
- `donald.py` - Expense tracking (uses `GastosTools`)
- `gastao.py` - Market opportunities
- `professor_pardal.py` - Automation/Google APIs (uses `GoogleIntegrationTools`)
- `ze_carioca.py` - International investments (uses `InternacionalTools`)
- `maga_patalojica.py` - Tax planning (uses `TributarioTools`)
- `tia_patilda.py` - Real assets & alternatives (uses `AtivosReaisTools`)
- `gizmoduck.py` - Crypto & blockchain risk (uses `CriptoTools`)
- `webby.py` - Credit card statements analysis (uses `CartoesTools`)

**Tools** (`tools/`): Classes with methods that provide concrete functionality. Tools return dictionaries with results and are independent/reusable.

**Team** (`team.py`): `criar_team_caixa_forte()` creates the coordinated team with all agents.

### External Integrations

- **yfinance**: Stock and FII price data
- **Google APIs** (OAuth 2.0): Gmail, Drive, Sheets - handles Rico brokerage email processing
- **BCB APIs**: SELIC and CDI rates

### Configuration

- `config/settings.py`: Agent personalities and settings
- `.env`: API keys (OPENAI_API_KEY required, ANTHROPIC_API_KEY optional), FOLDER_ID, SHEETS_ID, TELEGRAM_BOT_TOKEN
- `credentials.json` / `token.json`: Google OAuth authentication

### Telegram Bot

`telegram_bot.py` integrates the team with Telegram:
- Commands: `/start`, `/ajuda`, `/equipe`
- Messages are processed by the Caixa Forte team
- Requires `TELEGRAM_BOT_TOKEN` from @BotFather

## Code Patterns

**Adding a new agent:**
1. Create agent file in `agents/` with Agno `Agent` class
2. Define tools in `tools/` as a class with methods
3. Add agent to team in `team.py`

**Tool methods:**
- Return dictionaries with results
- Use Portuguese for user-facing strings
- Handle API errors gracefully

**Streaming responses:**
```python
agent.run("query", stream=True)
```

## Automation Flow (Professor Pardal)

```
Gmail (Rico emails) → Drive (save PDFs) → pdfplumber (parse) → Sheets (update records)
```

Logs to `scheduler.log` with UTF-8 encoding for Portuguese characters.
