"""
Schema de saída para o Huguinho - Especialista em Ações.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase, DadosAtivo


class IndicadoresAcao(BaseModel):
    """Indicadores fundamentalistas de uma ação."""
    ticker: str = Field(description="Código da ação (ex: PETR4.SA)")
    nome: Optional[str] = Field(default=None, description="Nome da empresa")
    preco_atual: Optional[float] = Field(default=None, description="Preço atual em reais")
    pl: Optional[float] = Field(default=None, description="Preço/Lucro (P/L)")
    pvp: Optional[float] = Field(default=None, description="Preço/Valor Patrimonial (P/VP)")
    dividend_yield: Optional[float] = Field(default=None, description="Dividend Yield anualizado (%)")
    roe: Optional[float] = Field(default=None, description="Return on Equity (%)")
    variacao_dia: Optional[float] = Field(default=None, description="Variação percentual no dia")


class RespostaAcoes(RespostaBase):
    """Resposta estruturada do Huguinho para análise de ações."""
    acoes_analisadas: Optional[list[IndicadoresAcao]] = Field(
        default=None, description="Lista de ações analisadas com indicadores"
    )
    comparativo: Optional[str] = Field(
        default=None, description="Texto comparativo entre ações analisadas"
    )
    melhor_opcao: Optional[str] = Field(
        default=None, description="Indicação da melhor opção com justificativa"
    )
