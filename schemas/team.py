"""
Schema de saída para o Team Caixa Forte.
"""
from typing import Optional
from pydantic import BaseModel, Field


class RespostaAgente(BaseModel):
    """Resumo da resposta de um agente consultado."""
    agente: str = Field(description="Nome do agente")
    resumo: str = Field(description="Resumo da contribuição do agente")


class RespostaCaixaForte(BaseModel):
    """Resposta estruturada do Team Caixa Forte."""
    resumo_executivo: str = Field(description="Resumo executivo da resposta (1-3 frases)")
    resposta_completa: str = Field(
        description="Resposta completa em Markdown com personalidade DuckTales"
    )
    agentes_consultados: Optional[list[RespostaAgente]] = Field(
        default=None, description="Agentes que contribuíram para a resposta"
    )
    proximos_passos: Optional[list[str]] = Field(
        default=None, description="Sugestões de próximos passos para o usuário"
    )
    aviso_legal: str = Field(
        default="Esta análise é meramente educativa e não constitui recomendação de investimento.",
        description="Aviso legal obrigatório"
    )
