"""
Schema de saída para o Zé Carioca - Especialista em Investimentos Internacionais.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class CotacaoMoeda(BaseModel):
    """Cotação de uma moeda."""
    moeda: str = Field(description="Nome/código da moeda (ex: USD, EUR)")
    cotacao: Optional[float] = Field(default=None, description="Cotação em reais")
    variacao_dia: Optional[float] = Field(default=None, description="Variação percentual no dia")


class ETFAnalisado(BaseModel):
    """Dados de um ETF internacional analisado."""
    ticker: str = Field(description="Código do ETF (ex: SPY, QQQ)")
    nome: Optional[str] = Field(default=None, description="Nome do ETF")
    preco_atual: Optional[float] = Field(default=None, description="Preço atual")
    regiao: Optional[str] = Field(default=None, description="Região/mercado que o ETF cobre")
    retorno_12m: Optional[float] = Field(default=None, description="Retorno nos últimos 12 meses (%)")


class RespostaInternacional(RespostaBase):
    """Resposta estruturada do Zé Carioca para investimentos internacionais."""
    cotacoes: Optional[list[CotacaoMoeda]] = Field(
        default=None, description="Cotações de moedas consultadas"
    )
    etfs_analisados: Optional[list[ETFAnalisado]] = Field(
        default=None, description="ETFs analisados"
    )
    sugestao_alocacao_global: Optional[str] = Field(
        default=None, description="Sugestão de alocação global"
    )
