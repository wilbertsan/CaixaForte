"""
Schema de saída para o Professor Pardal - Especialista em Automação.
"""
from typing import Optional
from pydantic import BaseModel, Field
from schemas.base import RespostaBase


class ResultadoFluxo(BaseModel):
    """Resultado do fluxo de automação."""
    emails_encontrados: Optional[int] = Field(default=None, description="Quantidade de emails encontrados")
    pdfs_processados: Optional[int] = Field(default=None, description="Quantidade de PDFs processados")
    negociacoes_registradas: Optional[int] = Field(default=None, description="Quantidade de negociações registradas")
    erros: Optional[list[str]] = Field(default=None, description="Lista de erros encontrados")


class RespostaAutomacao(RespostaBase):
    """Resposta estruturada do Professor Pardal para automação."""
    resultado_fluxo: Optional[ResultadoFluxo] = Field(
        default=None, description="Resultado do fluxo de automação"
    )
    status_conexao: Optional[str] = Field(
        default=None, description="Status da conexão com APIs do Google"
    )
    proximos_passos: Optional[list[str]] = Field(
        default=None, description="Próximos passos sugeridos"
    )
