"""
Tools para planejamento tributário de investimentos
Cálculos de IR, estratégias fiscais e otimização tributária
"""
from typing import List, Optional
from datetime import datetime, date


class TributarioTools:
    """Ferramentas para planejamento tributário e eficiência fiscal"""

    # Tabela regressiva de IR para Renda Fixa
    TABELA_IR_RENDA_FIXA = [
        {"ate_dias": 180, "aliquota": 22.5, "descricao": "Até 180 dias"},
        {"ate_dias": 360, "aliquota": 20.0, "descricao": "De 181 a 360 dias"},
        {"ate_dias": 720, "aliquota": 17.5, "descricao": "De 361 a 720 dias"},
        {"ate_dias": float('inf'), "aliquota": 15.0, "descricao": "Acima de 720 dias"}
    ]

    # Alíquotas por tipo de ativo
    ALIQUOTAS = {
        "acoes_swing_trade": 15.0,
        "acoes_day_trade": 20.0,
        "fiis": 20.0,
        "etfs_renda_variavel": 15.0,
        "bdrs": 15.0,
        "cripto": 15.0,
        "exterior_ate_5mi": 15.0,
        "exterior_acima_5mi": 22.5
    }

    # Limite de isenção mensal para ações
    LIMITE_ISENCAO_ACOES = 20000.0

    def calcular_ir_acoes(
        self,
        valor_venda: float,
        valor_compra: float,
        is_day_trade: bool = False,
        vendas_mes: float = 0
    ) -> dict:
        """
        Calcula o IR devido na venda de ações.

        Args:
            valor_venda: Valor total da venda
            valor_compra: Custo de aquisição (preço médio * quantidade)
            is_day_trade: Se é operação day trade
            vendas_mes: Total de vendas no mês (para verificar isenção)

        Returns:
            Dicionário com cálculo do IR
        """
        lucro = valor_venda - valor_compra
        total_vendas_mes = vendas_mes + valor_venda

        if is_day_trade:
            # Day trade: 20% sem isenção
            aliquota = self.ALIQUOTAS["acoes_day_trade"]
            isento = False
            ir_devido = max(0, lucro * (aliquota / 100)) if lucro > 0 else 0
            mensagem = "Day trade: 20% sobre o lucro, sem isenção"
        else:
            # Swing trade: 15% com isenção até R$ 20k/mês em vendas
            aliquota = self.ALIQUOTAS["acoes_swing_trade"]
            isento = total_vendas_mes <= self.LIMITE_ISENCAO_ACOES

            if isento and lucro > 0:
                ir_devido = 0
                mensagem = f"Isento! Vendas no mês (R$ {total_vendas_mes:,.2f}) abaixo de R$ 20.000"
            elif lucro > 0:
                ir_devido = lucro * (aliquota / 100)
                mensagem = f"Vendas no mês (R$ {total_vendas_mes:,.2f}) acima de R$ 20.000 - IR de 15% aplicável"
            else:
                ir_devido = 0
                mensagem = "Prejuízo - pode ser compensado em operações futuras"

        return {
            "tipo": "Day Trade" if is_day_trade else "Swing Trade",
            "valor_venda": valor_venda,
            "valor_compra": valor_compra,
            "lucro_prejuizo": round(lucro, 2),
            "aliquota": aliquota,
            "isento": isento,
            "ir_devido": round(ir_devido, 2),
            "total_vendas_mes": total_vendas_mes,
            "mensagem": mensagem,
            "dica": "Prejuízos podem ser compensados com lucros futuros do mesmo tipo (day trade com day trade, swing com swing)"
        }

    def calcular_ir_fiis(self, valor_venda: float, valor_compra: float) -> dict:
        """
        Calcula o IR na venda de FIIs.
        FIIs não têm isenção de R$ 20k - IR de 20% sobre qualquer lucro.

        Args:
            valor_venda: Valor total da venda
            valor_compra: Custo de aquisição

        Returns:
            Dicionário com cálculo do IR
        """
        lucro = valor_venda - valor_compra
        aliquota = self.ALIQUOTAS["fiis"]

        if lucro > 0:
            ir_devido = lucro * (aliquota / 100)
            mensagem = "FIIs: 20% sobre o lucro, sem isenção de R$ 20k"
        else:
            ir_devido = 0
            mensagem = "Prejuízo - pode ser compensado com lucros futuros em FIIs"

        return {
            "tipo": "FII",
            "valor_venda": valor_venda,
            "valor_compra": valor_compra,
            "lucro_prejuizo": round(lucro, 2),
            "aliquota": aliquota,
            "ir_devido": round(ir_devido, 2),
            "mensagem": mensagem,
            "lembrete": "Dividendos de FIIs são isentos de IR para pessoa física"
        }

    def calcular_ir_renda_fixa(
        self,
        valor_resgate: float,
        valor_aplicado: float,
        dias_aplicacao: int
    ) -> dict:
        """
        Calcula o IR na renda fixa usando a tabela regressiva.

        Args:
            valor_resgate: Valor do resgate
            valor_aplicado: Valor inicialmente aplicado
            dias_aplicacao: Dias corridos desde a aplicação

        Returns:
            Dicionário com cálculo do IR
        """
        rendimento = valor_resgate - valor_aplicado

        # Encontrar alíquota na tabela regressiva
        aliquota = 15.0  # padrão
        faixa = "Acima de 720 dias"
        for faixa_ir in self.TABELA_IR_RENDA_FIXA:
            if dias_aplicacao <= faixa_ir["ate_dias"]:
                aliquota = faixa_ir["aliquota"]
                faixa = faixa_ir["descricao"]
                break

        ir_devido = max(0, rendimento * (aliquota / 100))

        return {
            "tipo": "Renda Fixa",
            "valor_aplicado": valor_aplicado,
            "valor_resgate": valor_resgate,
            "rendimento_bruto": round(rendimento, 2),
            "dias_aplicacao": dias_aplicacao,
            "faixa_ir": faixa,
            "aliquota": aliquota,
            "ir_devido": round(ir_devido, 2),
            "rendimento_liquido": round(rendimento - ir_devido, 2),
            "dica": "Quanto mais tempo investido, menor a alíquota. Aguarde 720+ dias para 15%"
        }

    def calcular_ir_exterior(
        self,
        valor_venda_usd: float,
        valor_compra_usd: float,
        dolar_venda: float,
        dolar_compra: float,
        ganho_capital_anual: float = 0
    ) -> dict:
        """
        Calcula o IR sobre investimentos no exterior.

        Args:
            valor_venda_usd: Valor da venda em dólares
            valor_compra_usd: Custo de aquisição em dólares
            dolar_venda: Cotação do dólar na data da venda
            dolar_compra: Cotação do dólar na data da compra
            ganho_capital_anual: Ganhos já realizados no ano (para faixas)

        Returns:
            Dicionário com cálculo do IR
        """
        # Converter para reais
        valor_venda_brl = valor_venda_usd * dolar_venda
        valor_compra_brl = valor_compra_usd * dolar_compra
        lucro_brl = valor_venda_brl - valor_compra_brl

        # Isenção de até R$ 35.000 em vendas/mês
        isento = valor_venda_brl <= 35000

        # Alíquota progressiva baseada no ganho total anual
        ganho_total = ganho_capital_anual + lucro_brl
        if ganho_total <= 5000000:
            aliquota = 15.0
        elif ganho_total <= 10000000:
            aliquota = 17.5
        elif ganho_total <= 30000000:
            aliquota = 20.0
        else:
            aliquota = 22.5

        if isento and lucro_brl > 0:
            ir_devido = 0
            mensagem = f"Isento! Vendas no mês abaixo de R$ 35.000"
        elif lucro_brl > 0:
            ir_devido = lucro_brl * (aliquota / 100)
            mensagem = f"IR de {aliquota}% sobre ganho de capital"
        else:
            ir_devido = 0
            mensagem = "Prejuízo - pode ser compensado em operações futuras no exterior"

        return {
            "tipo": "Investimento no Exterior",
            "valor_venda_usd": valor_venda_usd,
            "valor_compra_usd": valor_compra_usd,
            "dolar_venda": dolar_venda,
            "dolar_compra": dolar_compra,
            "valor_venda_brl": round(valor_venda_brl, 2),
            "valor_compra_brl": round(valor_compra_brl, 2),
            "lucro_brl": round(lucro_brl, 2),
            "isento": isento,
            "aliquota": aliquota,
            "ir_devido": round(ir_devido, 2),
            "mensagem": mensagem,
            "aviso": "Ganho cambial também é tributável. Declare via GCAP da Receita Federal."
        }

    def simular_venda_otimizada(
        self,
        valor_total: float,
        custo_aquisicao: float,
        tipo_ativo: str = "acoes"
    ) -> dict:
        """
        Simula estratégia de venda fracionada para otimizar impostos.

        Args:
            valor_total: Valor total que deseja vender
            custo_aquisicao: Custo total de aquisição
            tipo_ativo: Tipo do ativo (acoes, fiis, exterior)

        Returns:
            Comparativo entre venda única e fracionada
        """
        lucro_total = valor_total - custo_aquisicao
        proporcao_lucro = lucro_total / valor_total if valor_total > 0 else 0

        if tipo_ativo.lower() == "acoes":
            # Venda única
            if valor_total <= self.LIMITE_ISENCAO_ACOES:
                ir_unica = 0
            else:
                ir_unica = lucro_total * 0.15 if lucro_total > 0 else 0

            # Venda fracionada (R$ 20k por mês)
            meses_necessarios = int(valor_total / self.LIMITE_ISENCAO_ACOES) + 1
            ir_fracionada = 0  # Sempre isento se vender até R$ 20k/mês

            economia = ir_unica - ir_fracionada

            return {
                "tipo_ativo": "Ações",
                "valor_total": valor_total,
                "lucro_total": round(lucro_total, 2),
                "cenario_venda_unica": {
                    "ir_devido": round(ir_unica, 2),
                    "lucro_liquido": round(lucro_total - ir_unica, 2)
                },
                "cenario_venda_fracionada": {
                    "vendas_por_mes": self.LIMITE_ISENCAO_ACOES,
                    "meses_necessarios": meses_necessarios,
                    "ir_devido": 0,
                    "lucro_liquido": round(lucro_total, 2)
                },
                "economia_fiscal": round(economia, 2),
                "recomendacao": f"Fracionando em {meses_necessarios} meses, você economiza R$ {economia:,.2f} em IR"
                if economia > 0 else "Venda única já está otimizada"
            }

        elif tipo_ativo.lower() == "exterior":
            # Limite de isenção: R$ 35k/mês
            limite = 35000
            if valor_total <= limite:
                ir_unica = 0
            else:
                ir_unica = lucro_total * 0.15 if lucro_total > 0 else 0

            meses_necessarios = int(valor_total / limite) + 1
            ir_fracionada = 0

            economia = ir_unica - ir_fracionada

            return {
                "tipo_ativo": "Investimento no Exterior",
                "valor_total": valor_total,
                "lucro_total": round(lucro_total, 2),
                "cenario_venda_unica": {
                    "ir_devido": round(ir_unica, 2)
                },
                "cenario_venda_fracionada": {
                    "vendas_por_mes": limite,
                    "meses_necessarios": meses_necessarios,
                    "ir_devido": 0
                },
                "economia_fiscal": round(economia, 2),
                "recomendacao": f"Fracionando em {meses_necessarios} meses, você economiza R$ {economia:,.2f}"
                if economia > 0 else "Venda única já está otimizada"
            }

        else:
            return {
                "tipo_ativo": tipo_ativo,
                "mensagem": "FIIs não têm isenção - não há benefício em fracionar vendas",
                "ir_devido": round(lucro_total * 0.20, 2) if lucro_total > 0 else 0
            }

    def calcular_compensacao_prejuizo(
        self,
        prejuizo_acumulado: float,
        lucro_atual: float,
        tipo: str = "swing_trade"
    ) -> dict:
        """
        Calcula compensação de prejuízos acumulados.

        Args:
            prejuizo_acumulado: Prejuízo acumulado de operações anteriores
            lucro_atual: Lucro da operação atual
            tipo: Tipo de operação (swing_trade, day_trade, fiis)

        Returns:
            Dicionário com cálculo da compensação
        """
        # Prejuízo só pode ser compensado com mesmo tipo
        lucro_tributavel = max(0, lucro_atual - prejuizo_acumulado)
        prejuizo_utilizado = min(prejuizo_acumulado, lucro_atual) if lucro_atual > 0 else 0
        prejuizo_restante = prejuizo_acumulado - prejuizo_utilizado

        aliquotas = {
            "swing_trade": 15.0,
            "day_trade": 20.0,
            "fiis": 20.0
        }
        aliquota = aliquotas.get(tipo, 15.0)

        ir_sem_compensacao = lucro_atual * (aliquota / 100) if lucro_atual > 0 else 0
        ir_com_compensacao = lucro_tributavel * (aliquota / 100)
        economia = ir_sem_compensacao - ir_com_compensacao

        return {
            "tipo_operacao": tipo,
            "prejuizo_acumulado": prejuizo_acumulado,
            "lucro_atual": lucro_atual,
            "prejuizo_utilizado": round(prejuizo_utilizado, 2),
            "prejuizo_restante": round(prejuizo_restante, 2),
            "lucro_tributavel": round(lucro_tributavel, 2),
            "aliquota": aliquota,
            "ir_sem_compensacao": round(ir_sem_compensacao, 2),
            "ir_com_compensacao": round(ir_com_compensacao, 2),
            "economia_fiscal": round(economia, 2),
            "regra": f"Prejuízo de {tipo} só compensa lucro de {tipo}. Não prescreve."
        }

    def explicar_come_cotas(self, valor_aplicado: float, rentabilidade_anual: float = 10) -> dict:
        """
        Explica o impacto do come-cotas em fundos de investimento.

        Args:
            valor_aplicado: Valor aplicado no fundo
            rentabilidade_anual: Rentabilidade esperada (% ao ano)

        Returns:
            Explicação e simulação do come-cotas
        """
        # Come-cotas: antecipação de IR em maio e novembro
        # Fundos de longo prazo: 15% | Fundos de curto prazo: 20%
        rendimento_semestral = valor_aplicado * (rentabilidade_anual / 100) / 2
        come_cotas_lp = rendimento_semestral * 0.15
        come_cotas_cp = rendimento_semestral * 0.20

        return {
            "o_que_e": "Come-cotas é a antecipação semestral do IR em fundos de investimento (maio e novembro)",
            "valor_aplicado": valor_aplicado,
            "rentabilidade_estimada_semestral": round(rendimento_semestral, 2),
            "come_cotas_fundo_longo_prazo": {
                "aliquota": "15%",
                "valor_semestral": round(come_cotas_lp, 2),
                "valor_anual": round(come_cotas_lp * 2, 2)
            },
            "come_cotas_fundo_curto_prazo": {
                "aliquota": "20%",
                "valor_semestral": round(come_cotas_cp, 2),
                "valor_anual": round(come_cotas_cp * 2, 2)
            },
            "impacto": "Reduz o efeito dos juros compostos pois o IR é antecipado",
            "alternativas_sem_come_cotas": [
                "ETFs de renda fixa (IR só no resgate)",
                "Tesouro Direto (IR só no resgate)",
                "Previdência Privada (IR só no resgate)",
                "CDBs, LCIs, LCAs (IR só no resgate ou isentos)"
            ],
            "dica": "Fundos com come-cotas perdem para alternativas sem come-cotas no longo prazo"
        }

    def listar_investimentos_isentos(self) -> dict:
        """
        Lista investimentos com benefícios fiscais ou isenção de IR.

        Returns:
            Dicionário com investimentos isentos e seus benefícios
        """
        return {
            "totalmente_isentos": {
                "LCI": {
                    "nome": "Letra de Crédito Imobiliário",
                    "beneficio": "Isento de IR para pessoa física",
                    "fgc": "Sim, até R$ 250.000 por CPF/instituição"
                },
                "LCA": {
                    "nome": "Letra de Crédito do Agronegócio",
                    "beneficio": "Isento de IR para pessoa física",
                    "fgc": "Sim, até R$ 250.000 por CPF/instituição"
                },
                "CRI": {
                    "nome": "Certificado de Recebíveis Imobiliários",
                    "beneficio": "Isento de IR para pessoa física",
                    "fgc": "Não"
                },
                "CRA": {
                    "nome": "Certificado de Recebíveis do Agronegócio",
                    "beneficio": "Isento de IR para pessoa física",
                    "fgc": "Não"
                },
                "Debentures_Incentivadas": {
                    "nome": "Debêntures de Infraestrutura",
                    "beneficio": "Isento de IR para pessoa física",
                    "fgc": "Não"
                },
                "Dividendos_Acoes": {
                    "nome": "Dividendos de Ações",
                    "beneficio": "Isentos de IR (por enquanto)",
                    "obs": "Pode mudar com reforma tributária"
                },
                "Dividendos_FIIs": {
                    "nome": "Dividendos de FIIs",
                    "beneficio": "Isentos de IR para pessoa física",
                    "requisitos": "FII com mais de 50 cotistas, negociado em bolsa"
                }
            },
            "com_isencao_condicional": {
                "Acoes_ate_20k": {
                    "beneficio": "Vendas até R$ 20.000/mês são isentas (swing trade)",
                    "obs": "Day trade não tem isenção"
                },
                "Exterior_ate_35k": {
                    "beneficio": "Vendas até R$ 35.000/mês são isentas",
                    "obs": "Válido para ações, ETFs, REITs no exterior"
                },
                "Poupanca": {
                    "beneficio": "Isenta de IR",
                    "obs": "Rentabilidade geralmente perde da inflação"
                }
            },
            "dica_maga": "Não é quanto você ganha, é quanto você mantém! Use investimentos isentos estrategicamente."
        }

    def calendario_fiscal(self) -> dict:
        """
        Retorna o calendário de obrigações fiscais do investidor.

        Returns:
            Calendário com datas importantes
        """
        ano_atual = datetime.now().year

        return {
            "mensal": {
                "DARF_renda_variavel": {
                    "vencimento": "Último dia útil do mês seguinte",
                    "quando": "Quando houver lucro tributável em ações (acima de R$ 20k/mês), FIIs, ETFs, BDRs",
                    "codigo_darf": "6015 (operações comuns) ou 8468 (day trade)"
                }
            },
            "semestral": {
                "come_cotas": {
                    "datas": "Último dia útil de maio e novembro",
                    "o_que": "Antecipação de IR em fundos de investimento"
                }
            },
            "anual": {
                "IRPF": {
                    "periodo": f"Março a maio de {ano_atual + 1}",
                    "o_que": "Declaração anual de Imposto de Renda",
                    "declarar": "Posições em 31/12, rendimentos, ganhos de capital"
                },
                "GCAP": {
                    "quando": "Mês seguinte à venda de ativos no exterior",
                    "o_que": "Programa de Ganho de Capital da Receita Federal"
                }
            },
            "dicas": [
                "Guarde todas as notas de corretagem",
                "Controle o preço médio de cada ativo",
                "Registre prejuízos para compensação futura",
                "Separe day trade de swing trade no controle"
            ]
        }
