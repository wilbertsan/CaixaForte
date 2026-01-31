"""
Schema de saída para o Gastão - Especialista em Oportunidades.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class Oportunidade(BaseModel):
    """Uma oportunidade de investimento identificada."""
    ticker: str = Field(description="Código do ativo")
    tipo: Optional[str] = Field(default=None, description="Tipo: ação ou FII")
    motivo: str = Field(description="Motivo pelo qual é uma oportunidade")
    risco: Optional[str] = Field(default=None, description="Nível de risco identificado")


class RespostaOportunidades(RespostaBase):
    """Resposta estruturada do Gastão para oportunidades de mercado."""
    oportunidades: Optional[list[Oportunidade]] = Field(
        default=None, description="Lista de oportunidades identificadas"
    )
    contexto_mercado: Optional[str] = Field(
        default=None, description="Contexto geral do mercado"
    )
