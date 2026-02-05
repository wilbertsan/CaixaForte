"""
Agendador de Tarefas - Caixa Forte
Executa o Professor Pardal automaticamente em horários programados
"""
import schedule
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def executar_professor_pardal():
    """Executa o fluxo completo do Professor Pardal"""
    logger.info("=" * 50)
    logger.info("Iniciando execução do Professor Pardal...")
    logger.info("=" * 50)

    try:
        from tools.google_integration import GoogleIntegrationTools

        tools = GoogleIntegrationTools()

        # 1. Verificar conexão
        logger.info("Verificando conexões...")
        status = tools.verificar_conexao()
        if status.get("status") == "erro":
            logger.error(f"Erro na conexão: {status}")
            return

        logger.info(f"Conexões OK: Gmail={status['gmail']}, Drive={status['drive']}, Sheets={status['sheets']}")

        # 2. Processar emails da Rico (todos, não apenas não lidos)
        logger.info("Processando emails da Rico...")
        resultado_emails = tools.processar_emails_rico(apenas_nao_lidos=False, limite=500)

        if "erro" in resultado_emails:
            logger.error(f"Erro ao processar emails: {resultado_emails['erro']}")
        else:
            logger.info(f"Emails encontrados: {resultado_emails.get('emails_encontrados', 0)}")
            logger.info(f"Arquivos enviados ao Drive: {resultado_emails.get('processados', 0)}")
            logger.info(f"Arquivos ignorados (já existem): {resultado_emails.get('ignorados', 0)}")

        # 3. Processar PDFs do Drive
        logger.info("Processando PDFs do Drive...")
        resultado_pdfs = tools.processar_pdfs_drive()

        if "erro" in resultado_pdfs:
            logger.error(f"Erro ao processar PDFs: {resultado_pdfs['erro']}")
        else:
            logger.info(f"PDFs processados: {resultado_pdfs.get('arquivos_processados', 0)} arquivos")
            logger.info(f"Total de negociações extraídas: {resultado_pdfs.get('total_negociacoes', 0)}")

        logger.info("Execução concluída com sucesso!")

    except Exception as e:
        logger.error(f"Erro na execução: {str(e)}", exc_info=True)


def main():
    """Função principal do agendador"""
    logger.info("=" * 60)
    logger.info("  CAIXA FORTE - Agendador de Tarefas")
    logger.info("  Professor Pardal em modo automático")
    logger.info("=" * 60)

    # Agendar execução diária às 10:00
    schedule.every().day.at("10:00").do(executar_professor_pardal)

    logger.info("Tarefa agendada: Professor Pardal às 10:00 todos os dias")
    logger.info("Pressione Ctrl+C para encerrar")
    logger.info("")

    # Mostrar próxima execução
    proxima = schedule.next_run()
    logger.info(f"Próxima execução: {proxima}")

    # Loop principal
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada 1 minuto
        except KeyboardInterrupt:
            logger.info("\nAgendador encerrado pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
