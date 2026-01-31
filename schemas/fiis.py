"""
Schema de saída para o Zezinho - Especialista em FIIs.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class IndicadoresFII(BaseModel):
    """Indicadores de um Fundo de Investimento Imobiliário."""
    ticker: str = Field(description="Código do FII (ex: HGLG11)")
    nome: Optional[str] = Field(default=None, description="Nome do fundo")
    preco_atual: Optional[float] = Field(default=None, description="Preço atual da cota")
    dividend_yield: Optional[float] = Field(default=None, description="Dividend Yield anualizado (%)")
    ultimo_dividendo: Optional[float] = Field(default=None, description="Último dividendo por cota (R$)")
    tipo_fii: Optional[str] = Field(default=None, description="Tipo: tijolo, papel, híbrido, FOF")


class ProjecaoRenda(BaseModel):
    """Projeção de renda passiva com FIIs."""
    quantidade_cotas: Optional[int] = Field(default=None, description="Quantidade de cotas")
    renda_mensal_estimada: Optional[float] = Field(default=None, description="Renda mensal estimada (R$)")
    renda_anual_estimada: Optional[float] = Field(default=None, description="Renda anual estimada (R$)")
    investimento_total: Optional[float] = Field(default=None, description="Valor total investido (R$)")


class RespostaFIIs(RespostaBase):
    """Resposta estruturada do Zezinho para análise de FIIs."""
    fiis_analisados: Optional[list[IndicadoresFII]] = Field(
        default=None, description="Lista de FIIs analisados"
    )
    projecao_renda: Optional[ProjecaoRenda] = Field(
        default=None, description="Projeção de renda passiva"
    )
    comparativo: Optional[str] = Field(
        default=None, description="Texto comparativo entre FIIs analisados"
    )
