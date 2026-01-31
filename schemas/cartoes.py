"""
Schema de saída para a Webby - Especialista em Cartões.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class GastoCartaoCategoria(BaseModel):
    """Gasto por categoria no cartão de crédito."""
    categoria: str = Field(description="Nome da categoria")
    valor: float = Field(description="Valor total na categoria (R$)")
    percentual: Optional[float] = Field(default=None, description="Percentual do total (%)")
    quantidade_transacoes: Optional[int] = Field(default=None, description="Quantidade de transações")


class AssinaturaDetectada(BaseModel):
    """Assinatura/recorrência detectada no extrato."""
    descricao: str = Field(description="Descrição da assinatura")
    valor: float = Field(description="Valor mensal (R$)")
    categoria: Optional[str] = Field(default=None, description="Categoria da assinatura")


class RespostaCartoes(RespostaBase):
    """Resposta estruturada da Webby para análise de cartões."""
    gastos_por_categoria: Optional[list[GastoCartaoCategoria]] = Field(
        default=None, description="Gastos organizados por categoria"
    )
    alertas: Optional[list[str]] = Field(
        default=None, description="Alertas identificados"
    )
    uso_limite_percentual: Optional[float] = Field(
        default=None, description="Percentual do limite utilizado (%)"
    )
    assinaturas_detectadas: Optional[list[AssinaturaDetectada]] = Field(
        default=None, description="Assinaturas/recorrências detectadas"
    )
