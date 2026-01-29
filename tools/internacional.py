"""
Tools para análise de investimentos internacionais
Dólar, ETFs globais, BDRs e diversificação geográfica
"""
import yfinance as yf
from typing import List, Optional


class InternacionalTools:
    """Ferramentas para investimentos internacionais e diversificação global"""

    # ETFs populares por região/estratégia
    ETFS_GLOBAIS = {
        "EUA": {
            "SPY": "S&P 500",
            "QQQ": "Nasdaq 100",
            "VTI": "Total Stock Market EUA",
            "IWM": "Russell 2000 (Small Caps)",
            "DIA": "Dow Jones"
        },
        "Europa": {
            "VGK": "Europa Total",
            "EZU": "Zona Euro",
            "EWG": "Alemanha",
            "EWU": "Reino Unido"
        },
        "Asia": {
            "EWJ": "Japão",
            "FXI": "China Large Cap",
            "EWY": "Coreia do Sul",
            "EWT": "Taiwan"
        },
        "Emergentes": {
            "VWO": "Mercados Emergentes Total",
            "EEM": "Mercados Emergentes iShares",
            "IEMG": "Mercados Emergentes Core"
        },
        "Global": {
            "VT": "Total World Stock",
            "ACWI": "All Country World Index",
            "VXUS": "Total Internacional (ex-EUA)"
        },
        "Setoriais": {
            "XLK": "Tecnologia EUA",
            "XLF": "Financeiro EUA",
            "XLE": "Energia EUA",
            "XLV": "Saúde EUA",
            "GLD": "Ouro",
            "SLV": "Prata"
        }
    }

    def get_dolar_cotacao(self) -> dict:
        """
        Obtém a cotação atual do dólar (USD/BRL).

        Returns:
            Dicionário com informações do dólar
        """
        try:
            usdbrl = yf.Ticker("USDBRL=X")
            info = usdbrl.info
            hist = usdbrl.history(period="1mo")

            preco_atual = info.get("regularMarketPrice", info.get("ask", "N/A"))

            # Calcular variação mensal
            variacao_mes = None
            if not hist.empty and len(hist) > 1:
                variacao_mes = round(((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100, 2)

            return {
                "par": "USD/BRL",
                "cotacao": preco_atual,
                "variacao_dia": info.get("regularMarketChangePercent", "N/A"),
                "maxima_dia": info.get("dayHigh", "N/A"),
                "minima_dia": info.get("dayLow", "N/A"),
                "max_52_semanas": info.get("fiftyTwoWeekHigh", "N/A"),
                "min_52_semanas": info.get("fiftyTwoWeekLow", "N/A"),
                "variacao_mes": variacao_mes,
                "mensagem": "Dólar comercial (taxa de câmbio USD/BRL)"
            }
        except Exception as e:
            return {"erro": str(e), "par": "USD/BRL"}

    def get_outras_moedas(self) -> dict:
        """
        Obtém cotações de outras moedas importantes em relação ao Real.

        Returns:
            Dicionário com cotações de moedas
        """
        moedas = {
            "EURBRL=X": "Euro",
            "GBPBRL=X": "Libra Esterlina",
            "JPYBRL=X": "Iene Japonês (x100)",
            "CHFBRL=X": "Franco Suíço",
            "CNYBRL=X": "Yuan Chinês"
        }

        resultados = []
        for ticker, nome in moedas.items():
            try:
                moeda = yf.Ticker(ticker)
                info = moeda.info
                resultados.append({
                    "moeda": nome,
                    "ticker": ticker.replace("=X", ""),
                    "cotacao": info.get("regularMarketPrice", info.get("ask", "N/A")),
                    "variacao_dia": info.get("regularMarketChangePercent", "N/A")
                })
            except:
                resultados.append({"moeda": nome, "erro": "Não disponível"})

        return {"moedas": resultados}

    def get_etf_info(self, ticker: str) -> dict:
        """
        Obtém informações detalhadas de um ETF internacional.

        Args:
            ticker: Código do ETF (ex: SPY, QQQ, VT)

        Returns:
            Dicionário com informações do ETF
        """
        try:
            etf = yf.Ticker(ticker)
            info = etf.info

            return {
                "ticker": ticker,
                "nome": info.get("longName", info.get("shortName", "N/A")),
                "preco_atual": info.get("regularMarketPrice", info.get("navPrice", "N/A")),
                "moeda": info.get("currency", "USD"),
                "variacao_dia": info.get("regularMarketChangePercent", "N/A"),
                "variacao_ytd": info.get("ytdReturn", "N/A"),
                "dividend_yield": info.get("yield", info.get("trailingAnnualDividendYield", "N/A")),
                "expense_ratio": info.get("annualReportExpenseRatio", "N/A"),
                "total_assets": info.get("totalAssets", "N/A"),
                "max_52_semanas": info.get("fiftyTwoWeekHigh", "N/A"),
                "min_52_semanas": info.get("fiftyTwoWeekLow", "N/A"),
                "categoria": info.get("category", "N/A"),
                "descricao": info.get("longBusinessSummary", "N/A")[:500] if info.get("longBusinessSummary") else "N/A"
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}

    def listar_etfs_por_regiao(self, regiao: str = None) -> dict:
        """
        Lista ETFs disponíveis por região/categoria.

        Args:
            regiao: Região específica (EUA, Europa, Asia, Emergentes, Global, Setoriais) ou None para todas

        Returns:
            Dicionário com ETFs listados
        """
        if regiao and regiao in self.ETFS_GLOBAIS:
            return {
                "regiao": regiao,
                "etfs": self.ETFS_GLOBAIS[regiao]
            }
        return {
            "todas_regioes": self.ETFS_GLOBAIS
        }

    def comparar_etfs(self, tickers: List[str], periodo: str = "1y") -> dict:
        """
        Compara performance de múltiplos ETFs.

        Args:
            tickers: Lista de códigos de ETFs
            periodo: Período de comparação (1mo, 3mo, 6mo, 1y, 2y, 5y)

        Returns:
            Dicionário com comparativo de performance
        """
        resultados = []
        for ticker in tickers:
            try:
                etf = yf.Ticker(ticker)
                hist = etf.history(period=periodo)
                info = etf.info

                if hist.empty:
                    resultados.append({"ticker": ticker, "erro": "Sem dados"})
                    continue

                variacao = round(((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100, 2)

                resultados.append({
                    "ticker": ticker,
                    "nome": info.get("shortName", "N/A"),
                    "preco_atual": round(hist['Close'].iloc[-1], 2),
                    "variacao_periodo": variacao,
                    "expense_ratio": info.get("annualReportExpenseRatio", "N/A"),
                    "dividend_yield": info.get("yield", "N/A")
                })
            except Exception as e:
                resultados.append({"ticker": ticker, "erro": str(e)})

        # Ordenar por performance
        resultados_validos = [r for r in resultados if "variacao_periodo" in r]
        resultados_validos.sort(key=lambda x: x["variacao_periodo"], reverse=True)

        return {
            "periodo": periodo,
            "comparativo": resultados_validos + [r for r in resultados if "erro" in r]
        }

    def get_bdr_info(self, ticker: str) -> dict:
        """
        Obtém informações de um BDR (Brazilian Depositary Receipt).
        BDRs permitem investir em empresas estrangeiras pela B3.

        Args:
            ticker: Código do BDR na B3 (ex: AAPL34, AMZO34, GOGL34)

        Returns:
            Dicionário com informações do BDR
        """
        try:
            # BDRs usam sufixo .SA
            ticker_sa = ticker if ticker.endswith(".SA") else f"{ticker}.SA"
            bdr = yf.Ticker(ticker_sa)
            info = bdr.info

            return {
                "ticker": ticker,
                "nome": info.get("longName", info.get("shortName", "N/A")),
                "preco_brl": info.get("regularMarketPrice", "N/A"),
                "variacao_dia": info.get("regularMarketChangePercent", "N/A"),
                "volume": info.get("volume", "N/A"),
                "max_52_semanas": info.get("fiftyTwoWeekHigh", "N/A"),
                "min_52_semanas": info.get("fiftyTwoWeekLow", "N/A"),
                "setor": info.get("sector", "N/A"),
                "pais_origem": info.get("country", "N/A"),
                "nota": "BDR negociado na B3 em Reais. Representa ações de empresa estrangeira."
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}

    def sugerir_diversificacao_global(self, perfil: str = "moderado") -> dict:
        """
        Sugere uma alocação de diversificação global baseada no perfil de risco.

        Args:
            perfil: conservador, moderado ou arrojado

        Returns:
            Dicionário com sugestão de alocação
        """
        alocacoes = {
            "conservador": {
                "descricao": "Foco em preservação com alguma exposição internacional",
                "alocacao": {
                    "Brasil (Renda Fixa)": "60%",
                    "Brasil (Renda Variável)": "15%",
                    "EUA (VTI/SPY)": "15%",
                    "Global/Emergentes (VT/VWO)": "5%",
                    "Ouro (GLD)": "5%"
                },
                "etfs_sugeridos": ["VTI", "VT", "GLD"]
            },
            "moderado": {
                "descricao": "Equilíbrio entre Brasil e exposição global",
                "alocacao": {
                    "Brasil (Renda Fixa)": "30%",
                    "Brasil (Renda Variável)": "25%",
                    "EUA (VTI/SPY)": "25%",
                    "Europa/Ásia (VGK/EWJ)": "10%",
                    "Emergentes (VWO)": "5%",
                    "Ouro (GLD)": "5%"
                },
                "etfs_sugeridos": ["VTI", "VGK", "VWO", "GLD"]
            },
            "arrojado": {
                "descricao": "Maior exposição internacional e crescimento",
                "alocacao": {
                    "Brasil (Renda Fixa)": "15%",
                    "Brasil (Renda Variável)": "20%",
                    "EUA (VTI + QQQ)": "35%",
                    "Europa/Ásia (VGK/EWJ)": "15%",
                    "Emergentes (VWO)": "10%",
                    "Setoriais/Temáticos": "5%"
                },
                "etfs_sugeridos": ["VTI", "QQQ", "VGK", "EWJ", "VWO"]
            }
        }

        perfil_lower = perfil.lower()
        if perfil_lower not in alocacoes:
            perfil_lower = "moderado"

        return {
            "perfil": perfil_lower,
            **alocacoes[perfil_lower],
            "aviso": "Esta é uma sugestão educacional. Consulte um profissional para decisões de investimento."
        }

    def analisar_exposicao_cambial(self, valor_brl: float, percentual_internacional: float = 30) -> dict:
        """
        Analisa a exposição cambial de uma carteira.

        Args:
            valor_brl: Valor total da carteira em Reais
            percentual_internacional: Percentual alocado em ativos internacionais

        Returns:
            Análise de exposição cambial
        """
        try:
            # Obter cotação atual do dólar
            usdbrl = yf.Ticker("USDBRL=X")
            dolar = usdbrl.info.get("regularMarketPrice", 5.0)

            valor_internacional = valor_brl * (percentual_internacional / 100)
            valor_em_dolar = valor_internacional / dolar

            # Simular cenários
            cenarios = {
                "dolar_sobe_10%": {
                    "nova_cotacao": round(dolar * 1.10, 2),
                    "valor_brl": round(valor_em_dolar * (dolar * 1.10), 2),
                    "ganho_cambial": round(valor_em_dolar * dolar * 0.10, 2)
                },
                "dolar_cai_10%": {
                    "nova_cotacao": round(dolar * 0.90, 2),
                    "valor_brl": round(valor_em_dolar * (dolar * 0.90), 2),
                    "perda_cambial": round(valor_em_dolar * dolar * 0.10, 2)
                }
            }

            return {
                "valor_total_carteira": valor_brl,
                "percentual_internacional": percentual_internacional,
                "valor_internacional_brl": round(valor_internacional, 2),
                "valor_internacional_usd": round(valor_em_dolar, 2),
                "cotacao_dolar_atual": dolar,
                "cenarios": cenarios,
                "analise": f"Com {percentual_internacional}% em ativos dolarizados, você tem proteção parcial contra desvalorização do Real."
            }
        except Exception as e:
            return {"erro": str(e)}
