"""
Tools para análise de investimentos em Renda Fixa
"""
import requests
from typing import Optional
from datetime import datetime, timedelta


class RendaFixaTools:
    """Ferramentas para análise de renda fixa brasileira"""

    def __init__(self):
        self.bcb_api = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{}/dados?formato=json"

    def get_selic(self) -> dict:
        """
        Obtém a taxa SELIC atual e histórico recente.

        Returns:
            Dicionário com informações da SELIC
        """
        try:
            # Série 432 - Taxa SELIC meta
            response = requests.get(self.bcb_api.format(432), timeout=10)
            data = response.json()

            if data:
                ultimo = data[-1]
                return {
                    "indicador": "SELIC Meta",
                    "taxa_atual": float(ultimo["valor"]),
                    "data": ultimo["data"],
                    "unidade": "% ao ano"
                }
            return {"erro": "Dados não disponíveis"}
        except Exception as e:
            return {"erro": str(e)}

    def get_cdi(self) -> dict:
        """
        Obtém a taxa CDI atual.

        Returns:
            Dicionário com informações do CDI
        """
        try:
            # Série 4389 - CDI diário
            response = requests.get(self.bcb_api.format(4389), timeout=10)
            data = response.json()

            if data:
                ultimo = data[-1]
                # CDI diário para anual (aproximação)
                cdi_diario = float(ultimo["valor"])
                cdi_anual = ((1 + cdi_diario/100) ** 252 - 1) * 100

                return {
                    "indicador": "CDI",
                    "taxa_diaria": cdi_diario,
                    "taxa_anual_estimada": round(cdi_anual, 2),
                    "data": ultimo["data"],
                    "unidade": "% ao dia / % ao ano"
                }
            return {"erro": "Dados não disponíveis"}
        except Exception as e:
            return {"erro": str(e)}

    def get_ipca(self) -> dict:
        """
        Obtém o IPCA acumulado 12 meses.

        Returns:
            Dicionário com informações do IPCA
        """
        try:
            # Série 433 - IPCA mensal
            response = requests.get(self.bcb_api.format(433), timeout=10)
            data = response.json()

            if data and len(data) >= 12:
                # Últimos 12 meses
                ultimos_12 = data[-12:]
                ipca_acum = 1
                for mes in ultimos_12:
                    ipca_acum *= (1 + float(mes["valor"])/100)
                ipca_acum = (ipca_acum - 1) * 100

                return {
                    "indicador": "IPCA",
                    "ultimo_mes": float(data[-1]["valor"]),
                    "acumulado_12m": round(ipca_acum, 2),
                    "data_ultimo": data[-1]["data"],
                    "unidade": "%"
                }
            return {"erro": "Dados não disponíveis"}
        except Exception as e:
            return {"erro": str(e)}

    def get_poupanca(self) -> dict:
        """
        Obtém o rendimento da poupança.

        Returns:
            Dicionário com informações da poupança
        """
        try:
            # Série 195 - Poupança (rendimento mensal)
            response = requests.get(self.bcb_api.format(195), timeout=10)
            data = response.json()

            if data:
                ultimo = data[-1]
                rend_mensal = float(ultimo["valor"])
                rend_anual = ((1 + rend_mensal/100) ** 12 - 1) * 100

                return {
                    "indicador": "Poupança",
                    "rendimento_mensal": rend_mensal,
                    "rendimento_anual_estimado": round(rend_anual, 2),
                    "data": ultimo["data"],
                    "unidade": "%"
                }
            return {"erro": "Dados não disponíveis"}
        except Exception as e:
            return {"erro": str(e)}

    def simulate_cdb(self, valor: float, taxa_cdi: float, percentual_cdi: float,
                     meses: int, ir_aplicavel: bool = True) -> dict:
        """
        Simula investimento em CDB.

        Args:
            valor: Valor a investir
            taxa_cdi: Taxa CDI anual (%)
            percentual_cdi: Percentual do CDI que o CDB paga (ex: 100 para 100% CDI)
            meses: Prazo em meses
            ir_aplicavel: Se deve calcular IR

        Returns:
            Dicionário com simulação
        """
        # Taxa efetiva
        taxa_efetiva_anual = taxa_cdi * (percentual_cdi / 100)
        taxa_mensal = ((1 + taxa_efetiva_anual/100) ** (1/12)) - 1

        # Valor bruto
        montante_bruto = valor * ((1 + taxa_mensal) ** meses)
        rendimento_bruto = montante_bruto - valor

        # Imposto de Renda (tabela regressiva)
        if ir_aplicavel:
            if meses <= 6:
                aliquota_ir = 0.225  # 22.5%
            elif meses <= 12:
                aliquota_ir = 0.20  # 20%
            elif meses <= 24:
                aliquota_ir = 0.175  # 17.5%
            else:
                aliquota_ir = 0.15  # 15%

            ir = rendimento_bruto * aliquota_ir
            rendimento_liquido = rendimento_bruto - ir
            montante_liquido = valor + rendimento_liquido
        else:
            ir = 0
            rendimento_liquido = rendimento_bruto
            montante_liquido = montante_bruto

        return {
            "valor_investido": valor,
            "prazo_meses": meses,
            "taxa_cdi": taxa_cdi,
            "percentual_cdi": percentual_cdi,
            "montante_bruto": round(montante_bruto, 2),
            "rendimento_bruto": round(rendimento_bruto, 2),
            "aliquota_ir": f"{aliquota_ir*100}%" if ir_aplicavel else "Isento",
            "imposto_renda": round(ir, 2),
            "rendimento_liquido": round(rendimento_liquido, 2),
            "montante_liquido": round(montante_liquido, 2),
            "rentabilidade_liquida_periodo": round((rendimento_liquido/valor)*100, 2)
        }

    def simulate_tesouro_selic(self, valor: float, taxa_selic: float, meses: int) -> dict:
        """
        Simula investimento no Tesouro SELIC.

        Args:
            valor: Valor a investir
            taxa_selic: Taxa SELIC anual (%)
            meses: Prazo em meses

        Returns:
            Dicionário com simulação
        """
        # Tesouro SELIC rende aproximadamente 100% da SELIC
        # Taxa de custódia B3: 0.20% ao ano sobre o excedente de R$ 10.000
        taxa_mensal = ((1 + taxa_selic/100) ** (1/12)) - 1

        montante_bruto = valor * ((1 + taxa_mensal) ** meses)
        rendimento_bruto = montante_bruto - valor

        # Taxa de custódia (simplificada)
        if valor > 10000:
            taxa_custodia = (valor - 10000) * 0.002 * (meses/12)
        else:
            taxa_custodia = 0

        # IR
        if meses <= 6:
            aliquota_ir = 0.225
        elif meses <= 12:
            aliquota_ir = 0.20
        elif meses <= 24:
            aliquota_ir = 0.175
        else:
            aliquota_ir = 0.15

        ir = rendimento_bruto * aliquota_ir
        rendimento_liquido = rendimento_bruto - ir - taxa_custodia
        montante_liquido = valor + rendimento_liquido

        return {
            "titulo": "Tesouro SELIC",
            "valor_investido": valor,
            "prazo_meses": meses,
            "taxa_selic": taxa_selic,
            "montante_bruto": round(montante_bruto, 2),
            "rendimento_bruto": round(rendimento_bruto, 2),
            "taxa_custodia_b3": round(taxa_custodia, 2),
            "aliquota_ir": f"{aliquota_ir*100}%",
            "imposto_renda": round(ir, 2),
            "rendimento_liquido": round(rendimento_liquido, 2),
            "montante_liquido": round(montante_liquido, 2)
        }

    def compare_investments(self, valor: float, meses: int) -> dict:
        """
        Compara diferentes opções de renda fixa.

        Args:
            valor: Valor a investir
            meses: Prazo em meses

        Returns:
            Comparativo entre opções
        """
        selic_info = self.get_selic()
        cdi_info = self.get_cdi()
        poupanca_info = self.get_poupanca()

        taxa_selic = selic_info.get("taxa_atual", 13.75)
        taxa_cdi = cdi_info.get("taxa_anual_estimada", 13.65)

        # Simulações
        tesouro = self.simulate_tesouro_selic(valor, taxa_selic, meses)
        cdb_100 = self.simulate_cdb(valor, taxa_cdi, 100, meses)
        cdb_110 = self.simulate_cdb(valor, taxa_cdi, 110, meses)

        # Poupança (isenta de IR)
        rend_poupanca_mensal = poupanca_info.get("rendimento_mensal", 0.5) / 100
        montante_poupanca = valor * ((1 + rend_poupanca_mensal) ** meses)

        return {
            "valor_investido": valor,
            "prazo_meses": meses,
            "indicadores_atuais": {
                "selic": taxa_selic,
                "cdi": taxa_cdi
            },
            "comparativo": [
                {
                    "produto": "Tesouro SELIC",
                    "montante_liquido": tesouro["montante_liquido"],
                    "rendimento_liquido": tesouro["rendimento_liquido"]
                },
                {
                    "produto": "CDB 100% CDI",
                    "montante_liquido": cdb_100["montante_liquido"],
                    "rendimento_liquido": cdb_100["rendimento_liquido"]
                },
                {
                    "produto": "CDB 110% CDI",
                    "montante_liquido": cdb_110["montante_liquido"],
                    "rendimento_liquido": cdb_110["rendimento_liquido"]
                },
                {
                    "produto": "Poupança",
                    "montante_liquido": round(montante_poupanca, 2),
                    "rendimento_liquido": round(montante_poupanca - valor, 2)
                }
            ]
        }
