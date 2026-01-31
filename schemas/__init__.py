"""
Schemas de saída estruturada para os agentes do Caixa Forte.
"""
from schemas.base import RespostaBase, DadosAtivo
from schemas.acoes import RespostaAcoes
from schemas.fiis import RespostaFIIs
from schemas.renda_fixa import RespostaRendaFixa
from schemas.gastos import RespostaGastos
from schemas.oportunidades import RespostaOportunidades
from schemas.automacao import RespostaAutomacao
from schemas.internacional import RespostaInternacional
from schemas.tributario import RespostaTributario
from schemas.ativos_reais import RespostaAtivosReais
from schemas.cripto import RespostaCripto
from schemas.cartoes import RespostaCartoes
from schemas.team import RespostaCaixaForte

__all__ = [
    "RespostaBase",
    "DadosAtivo",
    "RespostaAcoes",
    "RespostaFIIs",
    "RespostaRendaFixa",
    "RespostaGastos",
    "RespostaOportunidades",
    "RespostaAutomacao",
    "RespostaInternacional",
    "RespostaTributario",
    "RespostaAtivosReais",
    "RespostaCripto",
    "RespostaCartoes",
    "RespostaCaixaForte",
]
