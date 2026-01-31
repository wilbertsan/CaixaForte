"""
Caixa Forte - Sistema de Agentes Financeiros DuckTales

Execute este arquivo para iniciar o sistema de consultoria financeira.
"""
import warnings
warnings.filterwarnings("ignore", module="yfinance")

import os
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from team import criar_team_caixa_forte

# Carregar variáveis de ambiente
load_dotenv()

console = Console()


def exibir_boas_vindas():
    """Exibe mensagem de boas-vindas"""
    boas_vindas = """
# Bem-vindo à Caixa Forte!

Sua equipe de consultoria financeira DuckTales está pronta para ajudar!

## Nossa Equipe:

| Agente | Especialidade |
|--------|---------------|
| **Tio Patinhas** | Coordenador & Estrategista |
| **Huguinho** | Ações & Análise Fundamentalista |
| **Zezinho** | FIIs & Renda Passiva Imobiliária |
| **Luizinho** | Renda Fixa & Tesouro Direto |
| **Pato Donald** | Controle de Gastos & Orçamento |
| **Gastão** | Oportunidades de Mercado |
| **Professor Pardal** | Automação (Gmail, Drive, Planilhas) |
| **Zé Carioca** | Investimentos Internacionais & Dólar |
| **Maga Patológica** | Planejamento Tributário & IR |
| **Tia Patilda** | Imóveis & Ativos Reais |
| **Gizmoduck** | Criptoativos & Blockchain |
| **Webby** | Extratos de Cartões & Assinaturas |

Digite sua pergunta ou comando. Digite 'sair' para encerrar.
    """
    console.print(Panel(Markdown(boas_vindas), title="Caixa Forte", border_style="gold1"))


def exibir_exemplos():
    """Exibe exemplos de perguntas"""
    exemplos = """
## Exemplos de perguntas:

### Ações (Huguinho):
- "Qual o preço atual de PETR4?"
- "Analise os fundamentos de VALE3"

### FIIs (Zezinho):
- "Como está o dividend yield de HGLG11?"
- "Quanto renderia 100 cotas de MXRF11?"

### Renda Fixa (Luizinho):
- "Qual a taxa SELIC atual?"
- "Simule R$ 10.000 em CDB 100% CDI por 12 meses"

### Gastos (Donald):
- "Registre um gasto de R$ 150 em alimentação"
- "Qual meu resumo de gastos do mês?"

### Oportunidades (Gastão):
- "Quais ações parecem baratas no momento?"

### Automação (Professor Pardal):
- "Processar emails da Rico" (fluxo completo automático)
- "Diagnosticar emails da Rico"

### Internacional (Zé Carioca):
- "Qual a cotação do dólar?"
- "Compare os ETFs SPY e QQQ"
- "Como diversificar globalmente?"

### Tributário (Maga Patológica):
- "Quanto vou pagar de IR se vender R$ 50.000 em ações?"
- "Quais investimentos são isentos de IR?"
- "Como compensar prejuízos?"

### Imóveis (Tia Patilda):
- "Analise um imóvel de R$ 500.000 com aluguel de R$ 2.500"
- "Vale mais a pena comprar ou alugar?"
- "Simule um financiamento de R$ 600.000"

### Cripto (Gizmoduck):
- "Analise o Bitcoin como investimento"
- "A rede Ethereum é segura?"
- "Quanto de cripto devo ter na carteira?"

### Cartões (Webby):
- "Analise meu extrato do cartão"
- "Quais categorias de gasto você classifica?"
- "Meu limite é R$ 5.000 e a fatura R$ 3.500, está saudável?"
    """
    console.print(Panel(Markdown(exemplos), title="Exemplos", border_style="blue"))


def main():
    """Função principal - loop de interação"""
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Erro: OPENAI_API_KEY não configurada![/red]")
        console.print("Crie um arquivo .env com sua chave da OpenAI:")
        console.print("OPENAI_API_KEY=sua-chave-aqui")
        return

    exibir_boas_vindas()

    # Criar o time com sessão fixa para manter histórico entre execuções
    console.print("[yellow]Iniciando equipe...[/yellow]")
    team = criar_team_caixa_forte(
        session_id="main-cli",
        user_id="usuario-local",
    )
    console.print("[green]Equipe pronta![/green]\n")

    while True:
        try:
            # Obter input do usuário
            pergunta = console.input("[bold cyan]Você:[/bold cyan] ").strip()

            if not pergunta:
                continue

            if pergunta.lower() in ['sair', 'exit', 'quit']:
                console.print("\n[gold1]Tio Patinhas:[/gold1] Até a próxima! Lembre-se: cuide dos centavos que os reais cuidam de si mesmos!")
                break

            if pergunta.lower() in ['ajuda', 'help', 'exemplos']:
                exibir_exemplos()
                continue

            # Processar pergunta
            console.print("\n[dim]Consultando a equipe...[/dim]\n")

            # Usar o team para responder
            response = team.run(pergunta)

            # Exibir resposta
            if response and response.content:
                console.print(Panel(
                    Markdown(response.content),
                    title="Caixa Forte",
                    border_style="gold1"
                ))
            else:
                console.print("[yellow]Não foi possível obter uma resposta.[/yellow]")

            console.print()

        except KeyboardInterrupt:
            console.print("\n[gold1]Até a próxima![/gold1]")
            break
        except Exception as e:
            console.print(f"[red]Erro: {e}[/red]")


if __name__ == "__main__":
    main()
