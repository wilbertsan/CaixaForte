"""
Schema de saída para a Tia Patilda - Especialista em Ativos Reais.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class AnaliseImovel(BaseModel):
    """Análise de um imóvel para investimento."""
    valor_imovel: Optional[float] = Field(default=None, description="Valor do imóvel (R$)")
    aluguel_mensal: Optional[float] = Field(default=None, description="Aluguel mensal (R$)")
    yield_bruto: Optional[float] = Field(default=None, description="Yield bruto anual (%)")
    yield_liquido: Optional[float] = Field(default=None, description="Yield líquido estimado (%)")
    custos_adicionais: Optional[str] = Field(default=None, description="Custos adicionais identificados")


class SimulacaoFinanciamento(BaseModel):
    """Simulação de financiamento imobiliário."""
    valor_financiado: Optional[float] = Field(default=None, description="Valor financiado (R$)")
    prazo_meses: Optional[int] = Field(default=None, description="Prazo em meses")
    parcela_inicial: Optional[float] = Field(default=None, description="Valor da primeira parcela (R$)")
    custo_total: Optional[float] = Field(default=None, description="Custo total do financiamento (R$)")
    sistema: Optional[str] = Field(default=None, description="Sistema de amortização (SAC ou PRICE)")


class RespostaAtivosReais(RespostaBase):
    """Resposta estruturada da Tia Patilda para ativos reais."""
    analise_imovel: Optional[AnaliseImovel] = Field(
        default=None, description="Análise do imóvel"
    )
    financiamento: Optional[SimulacaoFinanciamento] = Field(
        default=None, description="Simulação de financiamento"
    )
    comparacao_fii_vs_imovel: Optional[str] = Field(
        default=None, description="Comparação entre FII e imóvel físico"
    )
