"""
Schema de saída para o Gizmoduck - Analista de Criptoativos.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class CriptoAnalisado(BaseModel):
    """Análise de um criptoativo."""
    nome: str = Field(description="Nome do criptoativo (ex: Bitcoin, Ethereum)")
    ticker: Optional[str] = Field(default=None, description="Ticker (ex: BTC, ETH)")
    preco_atual: Optional[float] = Field(default=None, description="Preço atual (USD)")
    classificacao_risco: Optional[str] = Field(
        default=None, description="Classificação: infraestrutura_base, expansao, experimental, inaceitavel"
    )
    nivel_seguranca: Optional[str] = Field(default=None, description="Avaliação de segurança da rede")
    exposicao_maxima_recomendada: Optional[float] = Field(
        default=None, description="Percentual máximo recomendado na carteira (%)"
    )


class RespostaCripto(RespostaBase):
    """Resposta estruturada do Gizmoduck para criptoativos."""
    criptos_analisados: Optional[list[CriptoAnalisado]] = Field(
        default=None, description="Criptoativos analisados"
    )
    recomendacao_custodia: Optional[str] = Field(
        default=None, description="Recomendação sobre custódia"
    )
