"""
Schema de saída para o Pato Donald - Especialista em Gastos.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class GastoPorCategoria(BaseModel):
    """Gasto em uma categoria específica."""
    categoria: str = Field(description="Nome da categoria")
    valor: float = Field(description="Valor total gasto (R$)")
    percentual: Optional[float] = Field(default=None, description="Percentual do total (%)")


class ResumoOrcamento(BaseModel):
    """Resumo do orçamento mensal."""
    receita_total: Optional[float] = Field(default=None, description="Receita total do mês (R$)")
    gasto_total: Optional[float] = Field(default=None, description="Gasto total do mês (R$)")
    saldo: Optional[float] = Field(default=None, description="Saldo (receita - gastos) (R$)")
    taxa_poupanca: Optional[float] = Field(default=None, description="Taxa de poupança (%)")


class RespostaGastos(RespostaBase):
    """Resposta estruturada do Donald para controle de gastos."""
    resumo_orcamento: Optional[ResumoOrcamento] = Field(
        default=None, description="Resumo do orçamento"
    )
    gastos_por_categoria: Optional[list[GastoPorCategoria]] = Field(
        default=None, description="Gastos organizados por categoria"
    )
    dicas_economia: Optional[list[str]] = Field(
        default=None, description="Dicas práticas de economia"
    )
    acao_realizada: Optional[str] = Field(
        default=None, description="Ação registrada (gasto, receita, orçamento)"
    )
