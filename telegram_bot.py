"""
Caixa Forte - Bot do Telegram
Integração do time DuckTales de consultoria financeira com Telegram
"""
import os
import logging
from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode, ChatAction

from team import criar_team_caixa_forte

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('telegram_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cache de times por usuário para manter memória individual
_teams: dict[str, object] = {}


def get_team(user_id: str, chat_id: str):
    """Retorna o time para o usuário, criando se necessário (lazy loading com memória por usuário)"""
    key = f"{user_id}_{chat_id}"
    if key not in _teams:
        logger.info(f"Criando time Caixa Forte para usuário {user_id}...")
        _teams[key] = criar_team_caixa_forte(
            session_id=f"telegram-{chat_id}",
            user_id=f"telegram-{user_id}",
        )
        logger.info(f"Time criado para usuário {user_id}!")
    return _teams[key]


# Mensagens
WELCOME_MESSAGE = """
🏦 *Bem-vindo à Caixa Forte\\!*

Sua equipe de consultoria financeira DuckTales está pronta\\!

*Nossa Equipe:*
🎩 *Tio Patinhas* \\- Coordenador
📈 *Huguinho* \\- Ações
🏢 *Zezinho* \\- FIIs
💰 *Luizinho* \\- Renda Fixa
🦆 *Pato Donald* \\- Gastos
🍀 *Gastão* \\- Oportunidades
🔧 *Professor Pardal* \\- Automação
🌎 *Zé Carioca* \\- Internacional
🧙‍♀️ *Maga Patológica* \\- Tributário
🏠 *Tia Patilda* \\- Imóveis
🤖 *Gizmoduck* \\- Cripto
🔍 *Webby* \\- Cartões

Digite sua pergunta ou use /ajuda para exemplos\\.
"""

HELP_MESSAGE = """
📚 *Exemplos de perguntas:*

*Ações \\(Huguinho\\):*
• Qual o preço de PETR4?
• Analise os fundamentos de VALE3

*FIIs \\(Zezinho\\):*
• Dividend yield de HGLG11?
• Analise MXRF11

*Renda Fixa \\(Luizinho\\):*
• Qual a taxa SELIC?
• Simule R$ 10\\.000 em CDB 100% CDI

*Gastos \\(Donald\\):*
• Registre gasto de R$ 150 em alimentação

*Internacional \\(Zé Carioca\\):*
• Cotação do dólar
• Compare ETFs SPY e QQQ

*Tributário \\(Maga Patológica\\):*
• IR sobre venda de R$ 50\\.000 em ações
• Investimentos isentos de IR

*Imóveis \\(Tia Patilda\\):*
• Analise imóvel de R$ 500k com aluguel de R$ 2\\.500
• Simule financiamento de R$ 600k

*Cripto \\(Gizmoduck\\):*
• Analise o Bitcoin
• Quanto de cripto ter na carteira?

*Cartões \\(Webby\\):*
• Analise meu extrato do cartão
• Meu limite é R$ 5\\.000 e a fatura R$ 3\\.500

*Comandos:*
/start \\- Iniciar
/ajuda \\- Esta mensagem
/equipe \\- Ver a equipe
"""

TEAM_MESSAGE = """
👥 *Equipe Caixa Forte*

🎩 *Tio Patinhas* \\- Coordenador & Estrategista
_"Cuide dos centavos que os reais cuidam de si mesmos\\!"_

📈 *Huguinho* \\- Ações & Análise Fundamentalista
_Analítico, focado em fundamentos_

🏢 *Zezinho* \\- FIIs & Renda Passiva
_Detalhista, focado em dividendos_

💰 *Luizinho* \\- Renda Fixa & Tesouro Direto
_Conservador, focado em segurança_

🦆 *Pato Donald* \\- Controle de Gastos
_Prático, focado no dia\\-a\\-dia_

🍀 *Gastão* \\- Oportunidades de Mercado
_Sortudo, observador de tendências_

🔧 *Professor Pardal* \\- Automação
_Inventivo, integra Gmail/Drive/Sheets_

🌎 *Zé Carioca* \\- Internacional & Dólar
_Cosmopolita, pensa fora da caixa_

🧙‍♀️ *Maga Patológica* \\- Planejamento Tributário
_"Não é quanto você ganha, é quanto você mantém\\!"_

🏠 *Tia Patilda* \\- Imóveis & Ativos Reais
_Prática, pensa em legado_

🤖 *Gizmoduck* \\- Cripto & Blockchain
_"Cripto é infraestrutura, não cassino\\!"_

🔍 *Webby* \\- Extratos de Cartões
_"Nenhum detalhe escapa da Webby\\!"_
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /start"""
    user = update.effective_user
    logger.info(f"Novo usuário: {user.username} ({user.id})")
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /ajuda"""
    await update.message.reply_text(
        HELP_MESSAGE,
        parse_mode=ParseMode.MARKDOWN_V2
    )


async def equipe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler para o comando /equipe"""
    await update.message.reply_text(
        TEAM_MESSAGE,
        parse_mode=ParseMode.MARKDOWN_V2
    )


def escape_markdown(text: str) -> str:
    """Escapa caracteres especiais do MarkdownV2"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


async def processar_mensagem(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa mensagens de texto e consulta o time"""
    user = update.effective_user
    mensagem = update.message.text

    logger.info(f"Mensagem de {user.username}: {mensagem[:50]}...")

    # Mostrar "digitando..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action=ChatAction.TYPING
    )

    try:
        # Obter o time com memória por usuário
        caixa_forte = get_team(
            user_id=str(user.id),
            chat_id=str(update.effective_chat.id),
        )

        # Processar a pergunta
        response = caixa_forte.run(mensagem)

        if response and response.content:
            resposta = response.content

            # Telegram tem limite de 4096 caracteres
            if len(resposta) > 4000:
                # Dividir em partes
                partes = [resposta[i:i+4000] for i in range(0, len(resposta), 4000)]
                for i, parte in enumerate(partes):
                    await update.message.reply_text(
                        f"📄 Parte {i+1}/{len(partes)}:\n\n{parte}"
                    )
            else:
                await update.message.reply_text(f"🏦 *Caixa Forte*\n\n{resposta}")
        else:
            await update.message.reply_text(
                "❌ Não consegui processar sua pergunta. Tente novamente."
            )

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        await update.message.reply_text(
            f"❌ Ocorreu um erro: {str(e)[:100]}\n\nTente novamente em alguns instantes."
        )


async def erro_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler de erros"""
    logger.error(f"Erro: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Ocorreu um erro inesperado. Tente novamente."
        )


async def post_init(application: Application) -> None:
    """Configurações pós-inicialização"""
    # Definir comandos do bot
    commands = [
        BotCommand("start", "Iniciar o bot"),
        BotCommand("ajuda", "Ver exemplos de perguntas"),
        BotCommand("equipe", "Conhecer a equipe"),
    ]
    await application.bot.set_my_commands(commands)
    logger.info("Comandos do bot configurados")


def main():
    """Função principal"""
    # Verificar token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Erro: TELEGRAM_BOT_TOKEN não configurado!")
        print("1. Crie um bot com @BotFather no Telegram")
        print("2. Copie o token e adicione ao .env:")
        print("   TELEGRAM_BOT_TOKEN=seu-token-aqui")
        return

    # Verificar OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Erro: OPENAI_API_KEY não configurada!")
        return

    print("🏦 Iniciando Caixa Forte Bot...")
    print("=" * 40)

    # Criar aplicação
    application = (
        Application.builder()
        .token(token)
        .post_init(post_init)
        .build()
    )

    # Adicionar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ajuda", ajuda))
    application.add_handler(CommandHandler("help", ajuda))
    application.add_handler(CommandHandler("equipe", equipe))
    application.add_handler(CommandHandler("team", equipe))

    # Handler para mensagens de texto
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, processar_mensagem)
    )

    # Handler de erros
    application.add_error_handler(erro_handler)

    # Iniciar bot
    print("✅ Bot iniciado! Pressione Ctrl+C para parar.")
    print("=" * 40)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
