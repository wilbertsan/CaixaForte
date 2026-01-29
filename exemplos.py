"""
Exemplos de uso dos agentes Caixa Forte

Este arquivo demonstra como usar os agentes individualmente
e como team.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def exemplo_agente_individual():
    """Exemplo de uso de um agente individual"""
    from agno.models.openai import OpenAIChat
    from agents.huguinho import criar_huguinho

    print("=" * 50)
    print("Exemplo: Usando Huguinho individualmente")
    print("=" * 50)

    # Criar o agente com modelo
    model = OpenAIChat(id="gpt-4o")
    huguinho = criar_huguinho(model=model)

    # Fazer uma pergunta
    response = huguinho.run("Analise os fundamentos de PETR4.SA")

    print(f"\nResposta do Huguinho:\n{response.content}")


def exemplo_team_completo():
    """Exemplo de uso do team completo"""
    from team import criar_team_caixa_forte

    print("\n" + "=" * 50)
    print("Exemplo: Usando o Team Caixa Forte")
    print("=" * 50)

    # Criar o time
    team = criar_team_caixa_forte()

    # Perguntas de exemplo
    perguntas = [
        "Qual a taxa SELIC atual?",
        "Quanto renderia R$ 10.000 em CDB 100% CDI por 12 meses?",
    ]

    for pergunta in perguntas:
        print(f"\nPergunta: {pergunta}")
        print("-" * 40)
        response = team.run(pergunta)
        print(f"Resposta: {response.content[:500]}...")


def exemplo_tools_direto():
    """Exemplo de uso das tools diretamente (sem agentes)"""
    from tools.renda_fixa import RendaFixaTools
    from tools.acoes import AcoesTools

    print("\n" + "=" * 50)
    print("Exemplo: Usando Tools diretamente")
    print("=" * 50)

    # Renda Fixa
    rf = RendaFixaTools()

    print("\n--- Taxa SELIC ---")
    selic = rf.get_selic()
    print(f"SELIC: {selic}")

    print("\n--- Simulação CDB ---")
    simulacao = rf.simulate_cdb(
        valor=10000,
        taxa_cdi=13.65,
        percentual_cdi=100,
        meses=12
    )
    print(f"Simulação: {simulacao}")

    # Ações
    acoes = AcoesTools()

    print("\n--- Preço PETR4 ---")
    preco = acoes.get_stock_price("PETR4.SA")
    print(f"PETR4: {preco}")


def exemplo_streaming():
    """Exemplo com streaming de resposta"""
    from team import criar_team_caixa_forte

    print("\n" + "=" * 50)
    print("Exemplo: Resposta com Streaming")
    print("=" * 50)

    team = criar_team_caixa_forte()

    print("\nPergunta: Quais são as melhores práticas para começar a investir?")
    print("-" * 40)
    print("Resposta: ", end="")

    # Usar streaming
    for chunk in team.run("Quais são as melhores práticas para começar a investir?", stream=True):
        if chunk.content:
            print(chunk.content, end="", flush=True)

    print("\n")


if __name__ == "__main__":
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Erro: Configure OPENAI_API_KEY no arquivo .env")
        exit(1)

    # Executar exemplos
    print("\n" + "=" * 60)
    print("  EXEMPLOS DE USO - CAIXA FORTE")
    print("=" * 60)

    # Exemplo sem precisar de API (tools diretas)
    exemplo_tools_direto()

    # Descomentar para testar com API:
    # exemplo_agente_individual()
    # exemplo_team_completo()
    # exemplo_streaming()
