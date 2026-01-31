"""
Schema de saída para a Maga Patológica - Especialista em Tributário.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class CalculoIR(BaseModel):
    """Cálculo de imposto de renda sobre investimentos."""
    tipo_investimento: str = Field(description="Tipo do investimento (ações, FIIs, renda fixa, exterior)")
    valor_venda: Optional[float] = Field(default=None, description="Valor total da venda (R$)")
    lucro: Optional[float] = Field(default=None, description="Lucro apurado (R$)")
    aliquota: Optional[float] = Field(default=None, description="Alíquota de IR aplicável (%)")
    imposto_devido: Optional[float] = Field(default=None, description="Imposto devido (R$)")
    isento: Optional[bool] = Field(default=None, description="Se a operação é isenta de IR")
    motivo_isencao: Optional[str] = Field(default=None, description="Motivo da isenção, se aplicável")


class EstrategiaFiscal(BaseModel):
    """Estratégia de otimização fiscal."""
    estrategia: str = Field(description="Descrição da estratégia")
    economia_estimada: Optional[float] = Field(default=None, description="Economia potencial (R$)")


class RespostaTributario(RespostaBase):
    """Resposta estruturada da Maga Patológica para planejamento tributário."""
    calculos_ir: Optional[list[CalculoIR]] = Field(
        default=None, description="Cálculos de IR realizados"
    )
    estrategias_fiscais: Optional[list[EstrategiaFiscal]] = Field(
        default=None, description="Estratégias de otimização fiscal"
    )
    economia_potencial: Optional[float] = Field(
        default=None, description="Economia total potencial (R$)"
    )
