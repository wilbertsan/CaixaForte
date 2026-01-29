"""
Tools para análise de ativos reais e investimentos alternativos
Imóveis físicos, terrenos, commodities e planejamento patrimonial
"""
import yfinance as yf
from typing import Optional, List


class AtivosReaisTools:
    """Ferramentas para análise de ativos reais e alternativos"""

    def analisar_imovel_aluguel(
        self,
        valor_imovel: float,
        aluguel_mensal: float,
        condominio: float = 0,
        iptu_anual: float = 0,
        vacancia_meses: int = 1,
        manutencao_anual_percentual: float = 1.0
    ) -> dict:
        """
        Analisa a rentabilidade de um imóvel para aluguel.

        Args:
            valor_imovel: Valor de mercado do imóvel
            aluguel_mensal: Valor do aluguel mensal bruto
            condominio: Valor do condomínio mensal (pago pelo proprietário se vago)
            iptu_anual: Valor do IPTU anual
            vacancia_meses: Estimativa de meses vagos por ano
            manutencao_anual_percentual: % do valor do imóvel gasto em manutenção/ano

        Returns:
            Análise completa de rentabilidade
        """
        # Receitas
        meses_ocupados = 12 - vacancia_meses
        receita_bruta_anual = aluguel_mensal * 12
        receita_liquida_anual = aluguel_mensal * meses_ocupados

        # Despesas
        condominio_anual = condominio * vacancia_meses  # Paga só quando vago
        manutencao_anual = valor_imovel * (manutencao_anual_percentual / 100)
        despesas_totais = condominio_anual + iptu_anual + manutencao_anual

        # Resultado
        resultado_liquido = receita_liquida_anual - despesas_totais

        # Yields
        yield_bruto = (receita_bruta_anual / valor_imovel) * 100
        yield_liquido = (resultado_liquido / valor_imovel) * 100
        cap_rate = yield_liquido  # Cap Rate = NOI / Valor do imóvel

        return {
            "valor_imovel": valor_imovel,
            "aluguel_mensal": aluguel_mensal,
            "receita": {
                "bruta_anual": receita_bruta_anual,
                "liquida_anual": round(receita_liquida_anual, 2),
                "meses_ocupados": meses_ocupados
            },
            "despesas": {
                "condominio_anual_vacancia": condominio_anual,
                "iptu_anual": iptu_anual,
                "manutencao_anual": round(manutencao_anual, 2),
                "total_anual": round(despesas_totais, 2)
            },
            "resultado_liquido_anual": round(resultado_liquido, 2),
            "resultado_liquido_mensal": round(resultado_liquido / 12, 2),
            "indicadores": {
                "yield_bruto": f"{yield_bruto:.2f}%",
                "yield_liquido": f"{yield_liquido:.2f}%",
                "cap_rate": f"{cap_rate:.2f}%"
            },
            "analise": self._classificar_yield(yield_liquido)
        }

    def _classificar_yield(self, yield_liquido: float) -> str:
        if yield_liquido >= 8:
            return "Excelente - yield acima da média do mercado"
        elif yield_liquido >= 6:
            return "Bom - yield competitivo com FIIs"
        elif yield_liquido >= 4:
            return "Regular - considere comparar com FIIs"
        else:
            return "Baixo - pode não compensar vs. outros investimentos"

    def comparar_compra_vs_aluguel(
        self,
        valor_imovel: float,
        aluguel_atual: float,
        entrada_percentual: float = 20,
        taxa_financiamento_anual: float = 10,
        prazo_anos: int = 30,
        valorizacao_anual: float = 4,
        rendimento_alternativo: float = 10
    ) -> dict:
        """
        Compara financeiramente comprar vs. alugar um imóvel.

        Args:
            valor_imovel: Valor do imóvel para compra
            aluguel_atual: Valor do aluguel mensal atual
            entrada_percentual: % de entrada
            taxa_financiamento_anual: Taxa de juros do financiamento (% ao ano)
            prazo_anos: Prazo do financiamento em anos
            valorizacao_anual: Expectativa de valorização do imóvel (% ao ano)
            rendimento_alternativo: Rendimento se investir a entrada (% ao ano)

        Returns:
            Comparativo detalhado
        """
        # Cálculos de compra
        entrada = valor_imovel * (entrada_percentual / 100)
        valor_financiado = valor_imovel - entrada
        taxa_mensal = (taxa_financiamento_anual / 100) / 12
        n_parcelas = prazo_anos * 12

        # Parcela (Price)
        if taxa_mensal > 0:
            parcela = valor_financiado * (taxa_mensal * (1 + taxa_mensal)**n_parcelas) / ((1 + taxa_mensal)**n_parcelas - 1)
        else:
            parcela = valor_financiado / n_parcelas

        total_pago = entrada + (parcela * n_parcelas)
        juros_totais = total_pago - valor_imovel

        # Valor futuro do imóvel
        valor_futuro_imovel = valor_imovel * ((1 + valorizacao_anual/100) ** prazo_anos)

        # Cenário aluguel + investimento
        custo_aluguel_total = aluguel_atual * 12 * prazo_anos  # Simplificado, sem reajuste

        # Se investisse a entrada
        entrada_investida = entrada * ((1 + rendimento_alternativo/100) ** prazo_anos)

        # Diferença mensal (parcela - aluguel) investida
        diferenca_mensal = parcela - aluguel_atual
        if diferenca_mensal > 0:
            # Taxa mensal de rendimento
            taxa_rend_mensal = (1 + rendimento_alternativo/100) ** (1/12) - 1
            # Valor futuro das diferenças investidas
            diferenca_investida = diferenca_mensal * (((1 + taxa_rend_mensal)**n_parcelas - 1) / taxa_rend_mensal)
        else:
            diferenca_investida = 0

        patrimonio_aluguel = entrada_investida + diferenca_investida

        return {
            "cenario_compra": {
                "valor_imovel": valor_imovel,
                "entrada": entrada,
                "valor_financiado": valor_financiado,
                "parcela_mensal": round(parcela, 2),
                "total_pago": round(total_pago, 2),
                "juros_pagos": round(juros_totais, 2),
                "valor_imovel_futuro": round(valor_futuro_imovel, 2),
                "patrimonio_final": round(valor_futuro_imovel, 2)
            },
            "cenario_aluguel": {
                "aluguel_mensal": aluguel_atual,
                "gasto_aluguel_total": round(custo_aluguel_total, 2),
                "entrada_investida_futuro": round(entrada_investida, 2),
                "diferenca_investida_futuro": round(diferenca_investida, 2),
                "patrimonio_final": round(patrimonio_aluguel, 2)
            },
            "comparativo": {
                "diferenca_patrimonio": round(valor_futuro_imovel - patrimonio_aluguel, 2),
                "melhor_opcao": "Comprar" if valor_futuro_imovel > patrimonio_aluguel else "Alugar",
                "prazo_anos": prazo_anos
            },
            "premissas": {
                "taxa_financiamento": f"{taxa_financiamento_anual}% a.a.",
                "valorizacao_imovel": f"{valorizacao_anual}% a.a.",
                "rendimento_investimentos": f"{rendimento_alternativo}% a.a."
            },
            "aviso": "Análise simplificada. Considere custos de transação, ITBI, escritura, manutenção, etc."
        }

    def simular_financiamento(
        self,
        valor_imovel: float,
        entrada_percentual: float = 20,
        taxa_anual: float = 10,
        prazo_anos: int = 30,
        sistema: str = "SAC"
    ) -> dict:
        """
        Simula um financiamento imobiliário.

        Args:
            valor_imovel: Valor do imóvel
            entrada_percentual: Percentual de entrada
            taxa_anual: Taxa de juros anual
            prazo_anos: Prazo em anos
            sistema: SAC ou PRICE

        Returns:
            Simulação do financiamento
        """
        entrada = valor_imovel * (entrada_percentual / 100)
        valor_financiado = valor_imovel - entrada
        taxa_mensal = (taxa_anual / 100) / 12
        n_parcelas = prazo_anos * 12

        if sistema.upper() == "SAC":
            # SAC: Amortização constante
            amortizacao = valor_financiado / n_parcelas
            primeira_parcela = amortizacao + (valor_financiado * taxa_mensal)
            ultima_parcela = amortizacao + (amortizacao * taxa_mensal)

            # Total pago (soma de PA)
            total_juros = (primeira_parcela - amortizacao + ultima_parcela - amortizacao) * n_parcelas / 2
            total_pago = valor_financiado + total_juros

            return {
                "sistema": "SAC (Amortização Constante)",
                "valor_imovel": valor_imovel,
                "entrada": entrada,
                "valor_financiado": valor_financiado,
                "taxa_anual": f"{taxa_anual}%",
                "prazo": f"{prazo_anos} anos ({n_parcelas} parcelas)",
                "primeira_parcela": round(primeira_parcela, 2),
                "ultima_parcela": round(ultima_parcela, 2),
                "amortizacao_mensal": round(amortizacao, 2),
                "total_juros": round(total_juros, 2),
                "total_pago": round(total_pago, 2),
                "caracteristica": "Parcelas decrescentes - começa mais alto e vai diminuindo"
            }
        else:
            # PRICE: Parcelas fixas
            if taxa_mensal > 0:
                parcela = valor_financiado * (taxa_mensal * (1 + taxa_mensal)**n_parcelas) / ((1 + taxa_mensal)**n_parcelas - 1)
            else:
                parcela = valor_financiado / n_parcelas

            total_pago = parcela * n_parcelas
            total_juros = total_pago - valor_financiado

            return {
                "sistema": "PRICE (Parcelas Fixas)",
                "valor_imovel": valor_imovel,
                "entrada": entrada,
                "valor_financiado": valor_financiado,
                "taxa_anual": f"{taxa_anual}%",
                "prazo": f"{prazo_anos} anos ({n_parcelas} parcelas)",
                "parcela_fixa": round(parcela, 2),
                "total_juros": round(total_juros, 2),
                "total_pago": round(total_pago, 2),
                "caracteristica": "Parcelas fixas durante todo o financiamento"
            }

    def comparar_fii_vs_imovel_fisico(
        self,
        valor_investimento: float,
        yield_fii: float = 8,
        yield_imovel: float = 5,
        liquidez_importante: bool = True
    ) -> dict:
        """
        Compara investir em FIIs vs. imóvel físico.

        Args:
            valor_investimento: Valor disponível para investir
            yield_fii: Dividend yield esperado do FII (% ao ano)
            yield_imovel: Yield líquido esperado do imóvel (% ao ano)
            liquidez_importante: Se liquidez é prioridade

        Returns:
            Comparativo detalhado
        """
        renda_fii_anual = valor_investimento * (yield_fii / 100)
        renda_imovel_anual = valor_investimento * (yield_imovel / 100)

        comparativo = {
            "valor_investimento": valor_investimento,
            "fii": {
                "renda_anual_estimada": round(renda_fii_anual, 2),
                "renda_mensal_estimada": round(renda_fii_anual / 12, 2),
                "yield": f"{yield_fii}%",
                "vantagens": [
                    "Alta liquidez - vende em segundos na bolsa",
                    "Diversificação - um FII pode ter vários imóveis",
                    "Gestão profissional",
                    "Baixo valor de entrada (a partir de ~R$ 100)",
                    "Dividendos isentos de IR para PF",
                    "Sem burocracia de inquilinos"
                ],
                "desvantagens": [
                    "Volatilidade de preço na bolsa",
                    "Não é um ativo tangível 'seu'",
                    "Risco de gestão do fundo",
                    "IR de 20% sobre ganho de capital"
                ]
            },
            "imovel_fisico": {
                "renda_anual_estimada": round(renda_imovel_anual, 2),
                "renda_mensal_estimada": round(renda_imovel_anual / 12, 2),
                "yield": f"{yield_imovel}%",
                "vantagens": [
                    "Ativo tangível - 'tijolo' real",
                    "Controle total sobre o patrimônio",
                    "Pode usar como garantia",
                    "Valorização por reformas",
                    "Legado para família",
                    "Proteção contra inflação histórica"
                ],
                "desvantagens": [
                    "Baixa liquidez - demora para vender",
                    "Concentração de risco em um único ativo",
                    "Custos de manutenção e vacância",
                    "Burocracia com inquilinos",
                    "ITBI, escritura, registro",
                    "Risco de inadimplência"
                ]
            },
            "diferenca_renda_anual": round(renda_fii_anual - renda_imovel_anual, 2),
            "recomendacao": self._recomendar_fii_ou_imovel(valor_investimento, liquidez_importante, yield_fii, yield_imovel)
        }

        return comparativo

    def _recomendar_fii_ou_imovel(self, valor: float, liquidez: bool, yield_fii: float, yield_imovel: float) -> str:
        if valor < 300000:
            return "Com este valor, FIIs oferecem melhor diversificação e acesso ao mercado imobiliário"
        elif liquidez:
            return "Se liquidez é prioridade, FIIs são mais adequados"
        elif yield_imovel > yield_fii:
            return "Se o yield do imóvel é maior e você aceita iliquidez, imóvel físico pode ser interessante"
        else:
            return "Considere um mix: FIIs para liquidez e renda, imóvel físico para legado"

    def analisar_terreno(
        self,
        valor_terreno: float,
        area_m2: float,
        valorizacao_anual_esperada: float = 5,
        anos_horizonte: int = 10,
        iptu_anual: float = 0
    ) -> dict:
        """
        Analisa investimento em terreno.

        Args:
            valor_terreno: Valor do terreno
            area_m2: Área em metros quadrados
            valorizacao_anual_esperada: Expectativa de valorização (% ao ano)
            anos_horizonte: Horizonte de investimento em anos
            iptu_anual: IPTU anual

        Returns:
            Análise do investimento em terreno
        """
        preco_m2 = valor_terreno / area_m2
        valor_futuro = valor_terreno * ((1 + valorizacao_anual_esperada/100) ** anos_horizonte)
        valorizacao_total = valor_futuro - valor_terreno
        custo_iptu_total = iptu_anual * anos_horizonte
        lucro_liquido = valorizacao_total - custo_iptu_total

        return {
            "terreno": {
                "valor_atual": valor_terreno,
                "area_m2": area_m2,
                "preco_m2": round(preco_m2, 2)
            },
            "projecao": {
                "horizonte_anos": anos_horizonte,
                "valorizacao_anual": f"{valorizacao_anual_esperada}%",
                "valor_futuro": round(valor_futuro, 2),
                "valorizacao_total": round(valorizacao_total, 2),
                "preco_m2_futuro": round(valor_futuro / area_m2, 2)
            },
            "custos": {
                "iptu_anual": iptu_anual,
                "iptu_total_periodo": custo_iptu_total
            },
            "resultado": {
                "lucro_bruto": round(valorizacao_total, 2),
                "lucro_liquido": round(lucro_liquido, 2),
                "rentabilidade_total": f"{((valor_futuro/valor_terreno) - 1) * 100:.1f}%"
            },
            "consideracoes": [
                "Terreno não gera renda passiva (a menos que alugue)",
                "Custo de oportunidade: dinheiro parado sem render",
                "Valorização depende muito da localização e desenvolvimento da região",
                "Pode ser usado para construção futura ou venda",
                "Proteção patrimonial de longo prazo"
            ]
        }

    def cotar_ouro(self) -> dict:
        """
        Obtém cotação atual do ouro.

        Returns:
            Cotação e informações sobre ouro
        """
        try:
            # Ouro em dólares
            ouro_usd = yf.Ticker("GC=F")
            info_usd = ouro_usd.info

            # Dólar
            usdbrl = yf.Ticker("USDBRL=X")
            dolar = usdbrl.info.get("regularMarketPrice", 5.0)

            preco_usd = info_usd.get("regularMarketPrice", info_usd.get("previousClose", 0))
            preco_brl = preco_usd * dolar

            # Histórico
            hist = ouro_usd.history(period="1y")
            variacao_ano = 0
            if not hist.empty and len(hist) > 1:
                variacao_ano = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100

            return {
                "ativo": "Ouro (Gold Futures)",
                "preco_onca_usd": round(preco_usd, 2),
                "preco_onca_brl": round(preco_brl, 2),
                "preco_grama_brl": round(preco_brl / 31.1035, 2),  # 1 onça = 31.1035 gramas
                "cotacao_dolar": round(dolar, 2),
                "variacao_12_meses": f"{variacao_ano:.1f}%",
                "caracteristicas": {
                    "reserva_valor": "Proteção contra inflação e crises",
                    "correlacao": "Geralmente descorrelacionado com bolsa",
                    "liquidez": "Alta liquidez global",
                    "formas_investir": ["ETF de ouro (ex: GOLD11)", "Ouro físico", "Contratos futuros"]
                }
            }
        except Exception as e:
            return {"erro": str(e)}

    def listar_ativos_alternativos(self) -> dict:
        """
        Lista opções de investimentos alternativos para diversificação.

        Returns:
            Lista de ativos alternativos
        """
        return {
            "commodities": {
                "ouro": {
                    "descricao": "Reserva de valor milenar",
                    "como_investir": ["ETF GOLD11", "Ouro físico", "Fundos de ouro"],
                    "perfil": "Proteção e diversificação"
                },
                "prata": {
                    "descricao": "Metal precioso com uso industrial",
                    "como_investir": ["ETF SLV (exterior)", "Prata física"],
                    "perfil": "Mais volátil que ouro"
                },
                "commodities_agricolas": {
                    "descricao": "Soja, milho, café, etc.",
                    "como_investir": ["Fundos de commodities", "ETFs setoriais"],
                    "perfil": "Exposição ao agronegócio"
                }
            },
            "imoveis_alternativos": {
                "terrenos": {
                    "descricao": "Valorização de longo prazo",
                    "perfil": "Baixa liquidez, sem renda passiva"
                },
                "imoveis_rurais": {
                    "descricao": "Fazendas, sítios, áreas agrícolas",
                    "perfil": "Arrendamento ou produção"
                },
                "garagens": {
                    "descricao": "Vagas de garagem em áreas nobres",
                    "perfil": "Ticket menor, boa rentabilidade"
                },
                "galpoes_logisticos": {
                    "descricao": "Imóveis para e-commerce e logística",
                    "perfil": "Setor em crescimento"
                }
            },
            "criptoativos": {
                "bitcoin": {
                    "descricao": "Reserva de valor digital",
                    "como_investir": ["Exchanges", "ETFs de cripto"],
                    "perfil": "Alta volatilidade, potencial reserva de valor"
                },
                "ethereum": {
                    "descricao": "Plataforma de contratos inteligentes",
                    "perfil": "Mais arriscado, foco em tecnologia"
                }
            },
            "outros": {
                "arte": {
                    "descricao": "Obras de arte e colecionáveis",
                    "perfil": "Baixíssima liquidez, para conhecedores"
                },
                "vinhos": {
                    "descricao": "Vinhos raros e safras especiais",
                    "perfil": "Nicho específico"
                },
                "royalties": {
                    "descricao": "Direitos musicais, patentes",
                    "perfil": "Renda passiva alternativa"
                }
            },
            "dica_tia_patilda": "Ativos reais atravessam gerações. Diversifique, mas foque no que você entende."
        }

    def calcular_patrimonio_multigeracional(
        self,
        patrimonio_atual: float,
        aporte_mensal: float,
        anos: int = 30,
        rendimento_anual: float = 8,
        inflacao_anual: float = 4
    ) -> dict:
        """
        Projeta crescimento patrimonial pensando em gerações.

        Args:
            patrimonio_atual: Patrimônio inicial
            aporte_mensal: Aporte mensal
            anos: Horizonte em anos
            rendimento_anual: Rendimento esperado (% ao ano)
            inflacao_anual: Inflação esperada (% ao ano)

        Returns:
            Projeção patrimonial
        """
        # Rendimento real (acima da inflação)
        rendimento_real = ((1 + rendimento_anual/100) / (1 + inflacao_anual/100) - 1) * 100
        taxa_mensal = (1 + rendimento_anual/100) ** (1/12) - 1

        # Valor futuro do patrimônio inicial
        vf_patrimonio = patrimonio_atual * ((1 + rendimento_anual/100) ** anos)

        # Valor futuro dos aportes (série de pagamentos)
        n_meses = anos * 12
        if taxa_mensal > 0:
            vf_aportes = aporte_mensal * (((1 + taxa_mensal)**n_meses - 1) / taxa_mensal)
        else:
            vf_aportes = aporte_mensal * n_meses

        patrimonio_futuro_nominal = vf_patrimonio + vf_aportes
        total_aportado = patrimonio_atual + (aporte_mensal * n_meses)

        # Valor em poder de compra atual (deflacionado)
        patrimonio_futuro_real = patrimonio_futuro_nominal / ((1 + inflacao_anual/100) ** anos)

        # Renda passiva estimada (4% ao ano - regra dos 4%)
        renda_passiva_mensal = (patrimonio_futuro_nominal * 0.04) / 12

        return {
            "situacao_atual": {
                "patrimonio_inicial": patrimonio_atual,
                "aporte_mensal": aporte_mensal
            },
            "premissas": {
                "horizonte_anos": anos,
                "rendimento_nominal": f"{rendimento_anual}% a.a.",
                "inflacao": f"{inflacao_anual}% a.a.",
                "rendimento_real": f"{rendimento_real:.1f}% a.a."
            },
            "projecao": {
                "total_aportado": round(total_aportado, 2),
                "patrimonio_futuro_nominal": round(patrimonio_futuro_nominal, 2),
                "patrimonio_futuro_real": round(patrimonio_futuro_real, 2),
                "ganho_total": round(patrimonio_futuro_nominal - total_aportado, 2)
            },
            "renda_passiva": {
                "regra_4_porcento": "Retirar 4% ao ano preserva o patrimônio",
                "renda_mensal_estimada": round(renda_passiva_mensal, 2),
                "renda_anual_estimada": round(renda_passiva_mensal * 12, 2)
            },
            "legado": {
                "mensagem": f"Em {anos} anos, você pode deixar R$ {patrimonio_futuro_nominal:,.0f} para as próximas gerações",
                "poder_compra_hoje": f"Equivale a R$ {patrimonio_futuro_real:,.0f} em valores de hoje"
            },
            "sabedoria_tia_patilda": "Patrimônio se constrói com paciência. Pense em décadas, não em meses."
        }
