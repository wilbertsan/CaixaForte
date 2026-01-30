"""
Team Caixa Forte - Equipe DuckTales de Consultoria Financeira

Este módulo configura o time completo de agentes financeiros
coordenados pelo Tio Patinhas.
"""
import os
from agno.team import Team
from agno.models.openai import OpenAIChat
from agno.db.sqlite import SqliteDb

from agents.tio_patinhas import criar_tio_patinhas
from agents.huguinho import criar_huguinho
from agents.zezinho import criar_zezinho
from agents.luizinho import criar_luizinho
from agents.donald import criar_donald
from agents.gastao import criar_gastao
from agents.professor_pardal import criar_professor_pardal
from agents.ze_carioca import criar_ze_carioca
from agents.maga_patalojica import criar_maga_patalojica
from agents.tia_patilda import criar_tia_patilda
from agents.gizmoduck import criar_gizmoduck
from agents.webby import criar_webby


def _get_db() -> SqliteDb:
    """Retorna a instância do banco SQLite para persistência."""
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, "caixa_forte.db")
    return SqliteDb(db_file=db_path)


def criar_team_caixa_forte(
    model_id: str = "gpt-4o-mini",
    session_id: str | None = None,
    user_id: str | None = None,
) -> Team:
    """
    Cria o time completo da Caixa Forte.

    Args:
        model_id: ID do modelo a ser usado (padrão: gpt-4o)
        session_id: ID da sessão para persistência de histórico
        user_id: ID do usuário para memória personalizada

    Returns:
        Team configurado com todos os agentes
    """
    # Configurar modelo
    model = OpenAIChat(id=model_id)

    # Configurar banco de dados e memória
    db = _get_db()

    # Criar os agentes especializados
    huguinho = criar_huguinho()
    zezinho = criar_zezinho()
    luizinho = criar_luizinho()
    donald = criar_donald()
    gastao = criar_gastao()
    professor_pardal = criar_professor_pardal()
    ze_carioca = criar_ze_carioca()
    maga_patalojica = criar_maga_patalojica()
    tia_patilda = criar_tia_patilda()
    gizmoduck = criar_gizmoduck()
    webby = criar_webby()

    # Instruções do time
    team_instructions = """
    Você é o sistema de coordenação da equipe "Caixa Forte", liderada pelo Tio Patinhas.

    ## Membros da Equipe:
    - **Huguinho**: Especialista em ações - consulte para análise de ações, indicadores fundamentalistas, dividendos de empresas
    - **Zezinho**: Especialista em FIIs - consulte para fundos imobiliários, dividend yield, renda passiva com FIIs
    - **Luizinho**: Especialista em renda fixa - consulte para Tesouro Direto, CDBs, taxas de juros, simulações de investimentos seguros
    - **Pato Donald**: Especialista em gastos - consulte para controle de orçamento, registro de gastos, análise de despesas
    - **Gastão**: Especialista em oportunidades - consulte para identificar boas oportunidades em ações e FIIs
    - **Professor Pardal**: Especialista em automação - consulte para processar emails da Rico, extrair notas de corretagem e atualizar planilhas
    - **Zé Carioca**: Especialista em investimentos internacionais - consulte para dólar, ETFs globais, BDRs, diversificação geográfica e proteção cambial
    - **Maga Patológica**: Especialista em planejamento tributário - consulte para cálculo de IR, estratégias fiscais, compensação de prejuízos, investimentos isentos
    - **Tia Patilda**: Especialista em ativos reais - consulte para imóveis físicos, terrenos, financiamento, ouro, investimentos alternativos, patrimônio multigeracional
    - **Gizmoduck**: Analista de criptoativos - consulte para Bitcoin, Ethereum, segurança de blockchain, protocolos DeFi, custódia, exposição a cripto
    - **Webby**: Analista de extratos de cartões - consulte para classificar gastos, detectar assinaturas, encontrar cobranças suspeitas, analisar uso do limite

    ## Regras de Delegação:
    1. Para perguntas sobre ações específicas → Huguinho
    2. Para perguntas sobre FIIs ou renda passiva imobiliária → Zezinho
    3. Para perguntas sobre renda fixa, SELIC, CDI, CDBs → Luizinho
    4. Para registro ou análise de gastos pessoais → Pato Donald
    5. Para buscar oportunidades de investimento → Gastão
    6. Para processar emails, PDFs ou atualizar planilhas → Professor Pardal
    7. Para dólar, ETFs globais, BDRs, investimentos internacionais, diversificação geográfica → Zé Carioca
    8. Para impostos, IR, planejamento tributário, isenções, compensação de prejuízos → Maga Patológica
    9. Para imóveis físicos, terrenos, financiamento, comprar vs alugar, ouro, ativos alternativos, legado → Tia Patilda
    10. Para criptomoedas, Bitcoin, Ethereum, blockchain, DeFi, segurança cripto, custódia → Gizmoduck
    11. Para extratos de cartão, classificar gastos, assinaturas, cobranças duplicadas, uso de limite → Webby
    12. Para perguntas gerais sobre estratégia → Coordene entre os especialistas

    ## Formato de Resposta:
    - Sempre comece identificando qual especialista está respondendo
    - Apresente as informações de forma clara e organizada
    - Quando múltiplos especialistas forem consultados, integre as respostas
    - Finalize com uma visão estratégica do Tio Patinhas quando apropriado

    ## Personalidade Geral:
    - Mantenha o tema DuckTales de forma divertida mas profissional
    - Use expressões características dos personagens ocasionalmente
    - Seja educativo e acessível
    - Nunca faça recomendações definitivas de investimento
    """

    # Criar o time com memória persistente
    team = Team(
        name="Caixa Forte",
        description="Equipe DuckTales de Consultoria Financeira",
        members=[huguinho, zezinho, luizinho, donald, gastao, professor_pardal, ze_carioca, maga_patalojica, tia_patilda, gizmoduck, webby],
        model=model,
        instructions=team_instructions,
        show_members_responses=True,
        # Persistência e memória
        session_id=session_id,
        user_id=user_id,
        db=db,
        enable_agentic_memory=True,
        add_history_to_context=True,
        num_history_runs=5,
    )

    return team


def criar_team_investimentos(model_id: str = "gpt-4o") -> Team:
    """
    Cria um sub-time focado apenas em investimentos.

    Args:
        model_id: ID do modelo

    Returns:
        Team de investimentos
    """
    model = OpenAIChat(id=model_id)

    huguinho = criar_huguinho()
    zezinho = criar_zezinho()
    luizinho = criar_luizinho()

    team = Team(
        name="Time de Investimentos",
        description="Especialistas em diferentes classes de ativos",
        members=[huguinho, zezinho, luizinho],
        model=model,
        instructions="""
        Time focado em análise de investimentos.
        - Huguinho: Ações
        - Zezinho: FIIs
        - Luizinho: Renda Fixa

        Delegue para o especialista correto baseado na classe de ativo.
        """
    )

    return team
