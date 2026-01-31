"""
Schema de saída para o Luizinho - Especialista em Renda Fixa.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class TaxasAtuais(BaseModel):
    """Taxas de referência atuais."""
    selic: Optional[float] = Field(default=None, description="Taxa SELIC anual (%)")
    cdi: Optional[float] = Field(default=None, description="Taxa CDI anual (%)")
    ipca: Optional[float] = Field(default=None, description="IPCA acumulado 12 meses (%)")


class SimulacaoRendaFixa(BaseModel):
    """Simulação de investimento em renda fixa."""
    produto: str = Field(description="Nome do produto (ex: CDB 100% CDI, Tesouro SELIC)")
    valor_investido: Optional[float] = Field(default=None, description="Valor investido (R$)")
    prazo_meses: Optional[int] = Field(default=None, description="Prazo em meses")
    rendimento_bruto: Optional[float] = Field(default=None, description="Rendimento bruto (R$)")
    rendimento_liquido: Optional[float] = Field(default=None, description="Rendimento líquido após IR (R$)")
    aliquota_ir: Optional[float] = Field(default=None, description="Alíquota de IR aplicada (%)")


class RespostaRendaFixa(RespostaBase):
    """Resposta estruturada do Luizinho para análise de renda fixa."""
    taxas_atuais: Optional[TaxasAtuais] = Field(
        default=None, description="Taxas de referência atuais"
    )
    simulacoes: Optional[list[SimulacaoRendaFixa]] = Field(
        default=None, description="Simulações de investimento realizadas"
    )
