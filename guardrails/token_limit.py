"""
Guardrail para limite de tokens de entrada.
"""
import tiktoken
from typing import Union
from agno.guardrails import BaseGuardrail
from agno.run.agent import RunInput
from agno.run.team import TeamRunInput
from agno.exceptions import InputCheckError, CheckTrigger


class TokenLimitGuardrail(BaseGuardrail):
    """
    Guardrail que limita o número de tokens na mensagem de entrada.

    Usa tiktoken para contagem precisa de tokens compatível com OpenAI.
    """

    def __init__(
        self,
        max_input_tokens: int = 4096,
        encoding_name: str = "cl100k_base",
    ):
        """
        Args:
            max_input_tokens: Número máximo de tokens permitidos na entrada
            encoding_name: Nome do encoding tiktoken (cl100k_base para GPT-4/GPT-3.5)
        """
        self.max_input_tokens = max_input_tokens
        self.encoding = tiktoken.get_encoding(encoding_name)

    def _count_tokens(self, text: str) -> int:
        """Conta tokens em um texto."""
        return len(self.encoding.encode(text))

    def _extract_message(self, run_input: Union[RunInput, TeamRunInput]) -> str:
        """Extrai a mensagem do input."""
        return run_input.input_content_string()

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Verifica se a entrada excede o limite de tokens."""
        message = self._extract_message(run_input)
        token_count = self._count_tokens(message)

        if token_count > self.max_input_tokens:
            raise InputCheckError(
                message=f"Mensagem excede o limite de {self.max_input_tokens} tokens. "
                        f"Sua mensagem tem {token_count} tokens. "
                        f"Por favor, reduza o tamanho da mensagem.",
                check_trigger=CheckTrigger.VALIDATION_FAILED,
                additional_data={
                    "token_count": token_count,
                    "max_tokens": self.max_input_tokens,
                },
            )

    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Versão assíncrona do check."""
        self.check(run_input)
