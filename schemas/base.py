"""
Schemas base compartilhados por todos os agentes.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


class DadosAtivo(BaseModel):
    """Dados básicos de um ativo financeiro."""
    ticker: str = Field(description="Código do ativo (ex: PETR4.SA, HGLG11)")
    nome: Optional[str] = Field(default=None, description="Nome do ativo ou empresa")
    preco_atual: Optional[float] = Field(default=None, description="Preço atual em reais")
    variacao_dia: Optional[float] = Field(default=None, description="Variação percentual no dia")


class RespostaBase(BaseModel):
    """Schema base para todas as respostas dos agentes."""
    agente: str = Field(description="Nome do agente que gerou a resposta")
    resumo: str = Field(description="Resumo curto da análise (1-2 frases)")
    analise: str = Field(description="Análise completa com personalidade DuckTales em Markdown")
    confianca: Literal["alto", "medio", "baixo"] = Field(description="Nível de confiança na análise: alto, medio ou baixo")
    aviso_legal: str = Field(
        default="Esta análise é meramente educativa e não constitui recomendação de investimento.",
        description="Aviso legal obrigatório"
    )
