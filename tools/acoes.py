"""
Tools para análise de ações brasileiras e internacionais
"""
import yfinance as yf
import pandas as pd
from typing import Optional, List


class AcoesTools:
    """Ferramentas para análise de ações"""

    def get_stock_price(self, ticker: str) -> dict:
        """
        Obtém o preço atual de uma ação.
        Para ações brasileiras, adicione .SA (ex: PETR4.SA)

        Args:
            ticker: Código da ação (ex: PETR4.SA, VALE3.SA, AAPL)

        Returns:
            Dicionário com informações do preço
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                "ticker": ticker,
                "nome": info.get("longName", "N/A"),
                "preco_atual": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                "variacao_dia": info.get("regularMarketChangePercent", "N/A"),
                "volume": info.get("volume", "N/A"),
                "max_52_semanas": info.get("fiftyTwoWeekHigh", "N/A"),
                "min_52_semanas": info.get("fiftyTwoWeekLow", "N/A"),
                "moeda": info.get("currency", "N/A")
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}

    def get_stock_fundamentals(self, ticker: str) -> dict:
        """
        Obtém indicadores fundamentalistas de uma ação.

        Args:
            ticker: Código da ação

        Returns:
            Dicionário com indicadores fundamentalistas
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                "ticker": ticker,
                "nome": info.get("longName", "N/A"),
                "setor": info.get("sector", "N/A"),
                "industria": info.get("industry", "N/A"),
                "p_l": info.get("trailingPE", "N/A"),
                "p_vp": info.get("priceToBook", "N/A"),
                "dividend_yield": info.get("dividendYield", "N/A"),
                "roe": info.get("returnOnEquity", "N/A"),
                "margem_liquida": info.get("profitMargins", "N/A"),
                "divida_patrimonio": info.get("debtToEquity", "N/A"),
                "valor_mercado": info.get("marketCap", "N/A"),
                "lpa": info.get("trailingEps", "N/A"),
                "vpa": info.get("bookValue", "N/A")
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}

    def get_stock_history(self, ticker: str, period: str = "1mo") -> dict:
        """
        Obtém histórico de preços de uma ação.

        Args:
            ticker: Código da ação
            period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            Dicionário com histórico resumido
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                return {"erro": "Sem dados históricos", "ticker": ticker}

            return {
                "ticker": ticker,
                "periodo": period,
                "preco_inicial": round(hist['Close'].iloc[0], 2),
                "preco_final": round(hist['Close'].iloc[-1], 2),
                "variacao_percentual": round(((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100, 2),
                "preco_maximo": round(hist['High'].max(), 2),
                "preco_minimo": round(hist['Low'].min(), 2),
                "volume_medio": int(hist['Volume'].mean()),
                "num_pregoes": len(hist)
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}

    def compare_stocks(self, tickers: List[str]) -> List[dict]:
        """
        Compara múltiplas ações.

        Args:
            tickers: Lista de códigos de ações

        Returns:
            Lista com comparativo das ações
        """
        results = []
        for ticker in tickers:
            fundamentals = self.get_stock_fundamentals(ticker)
            results.append(fundamentals)
        return results

    def get_dividends(self, ticker: str) -> dict:
        """
        Obtém histórico de dividendos de uma ação.

        Args:
            ticker: Código da ação

        Returns:
            Dicionário com informações de dividendos
        """
        try:
            stock = yf.Ticker(ticker)
            dividends = stock.dividends

            if dividends.empty:
                return {"ticker": ticker, "mensagem": "Sem histórico de dividendos"}

            # Últimos 12 meses de dividendos
            last_year = dividends.last('365D')

            return {
                "ticker": ticker,
                "total_dividendos_12m": round(last_year.sum(), 2) if not last_year.empty else 0,
                "num_pagamentos_12m": len(last_year),
                "ultimo_dividendo": round(dividends.iloc[-1], 4) if not dividends.empty else 0,
                "data_ultimo_dividendo": str(dividends.index[-1].date()) if not dividends.empty else "N/A"
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}
