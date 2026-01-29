"""
Tools para análise de Fundos de Investimento Imobiliário (FIIs)
"""
import yfinance as yf
from typing import Optional, List


class FIIsTools:
    """Ferramentas para análise de FIIs brasileiros"""

    def get_fii_price(self, ticker: str) -> dict:
        """
        Obtém o preço atual de um FII.
        FIIs brasileiros terminam com 11 (ex: HGLG11.SA)

        Args:
            ticker: Código do FII (ex: HGLG11.SA, XPML11.SA)

        Returns:
            Dicionário com informações do preço
        """
        # Garante que tem o sufixo .SA
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"

        try:
            fii = yf.Ticker(ticker)
            info = fii.info

            return {
                "ticker": ticker.replace('.SA', ''),
                "nome": info.get("longName", info.get("shortName", "N/A")),
                "preco_atual": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
                "variacao_dia": info.get("regularMarketChangePercent", "N/A"),
                "volume": info.get("volume", "N/A"),
                "max_52_semanas": info.get("fiftyTwoWeekHigh", "N/A"),
                "min_52_semanas": info.get("fiftyTwoWeekLow", "N/A")
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}

    def get_fii_dividends(self, ticker: str) -> dict:
        """
        Obtém histórico de dividendos de um FII.

        Args:
            ticker: Código do FII

        Returns:
            Dicionário com informações de dividendos
        """
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"

        try:
            fii = yf.Ticker(ticker)
            dividends = fii.dividends
            info = fii.info

            if dividends.empty:
                return {"ticker": ticker.replace('.SA', ''), "mensagem": "Sem histórico de dividendos"}

            # Últimos 12 meses
            last_year = dividends.last('365D')
            preco_atual = info.get("currentPrice", info.get("regularMarketPrice", 0))

            total_div_12m = last_year.sum() if not last_year.empty else 0
            dy_anual = (total_div_12m / preco_atual * 100) if preco_atual and preco_atual > 0 else 0

            return {
                "ticker": ticker.replace('.SA', ''),
                "preco_atual": preco_atual,
                "total_dividendos_12m": round(total_div_12m, 2),
                "dividend_yield_anual": round(dy_anual, 2),
                "num_pagamentos_12m": len(last_year),
                "media_mensal": round(total_div_12m / 12, 2),
                "ultimo_dividendo": round(dividends.iloc[-1], 4) if not dividends.empty else 0,
                "data_ultimo_dividendo": str(dividends.index[-1].date()) if not dividends.empty else "N/A"
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}

    def get_fii_history(self, ticker: str, period: str = "1y") -> dict:
        """
        Obtém histórico de preços de um FII.

        Args:
            ticker: Código do FII
            period: Período (1mo, 3mo, 6mo, 1y, 2y, 5y)

        Returns:
            Dicionário com histórico resumido
        """
        if not ticker.endswith('.SA'):
            ticker = f"{ticker}.SA"

        try:
            fii = yf.Ticker(ticker)
            hist = fii.history(period=period)

            if hist.empty:
                return {"erro": "Sem dados históricos", "ticker": ticker}

            return {
                "ticker": ticker.replace('.SA', ''),
                "periodo": period,
                "preco_inicial": round(hist['Close'].iloc[0], 2),
                "preco_final": round(hist['Close'].iloc[-1], 2),
                "variacao_percentual": round(((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100, 2),
                "preco_maximo": round(hist['High'].max(), 2),
                "preco_minimo": round(hist['Low'].min(), 2),
                "volume_medio": int(hist['Volume'].mean())
            }
        except Exception as e:
            return {"erro": str(e), "ticker": ticker}

    def compare_fiis(self, tickers: List[str]) -> List[dict]:
        """
        Compara múltiplos FIIs pelo dividend yield.

        Args:
            tickers: Lista de códigos de FIIs

        Returns:
            Lista com comparativo dos FIIs ordenado por DY
        """
        results = []
        for ticker in tickers:
            div_info = self.get_fii_dividends(ticker)
            if "erro" not in div_info:
                results.append(div_info)

        # Ordena por dividend yield
        results.sort(key=lambda x: x.get("dividend_yield_anual", 0), reverse=True)
        return results

    def calculate_income(self, ticker: str, cotas: int) -> dict:
        """
        Calcula a renda mensal estimada com base nas cotas.

        Args:
            ticker: Código do FII
            cotas: Número de cotas

        Returns:
            Dicionário com estimativa de renda
        """
        div_info = self.get_fii_dividends(ticker)

        if "erro" in div_info:
            return div_info

        media_mensal = div_info.get("media_mensal", 0)
        preco_atual = div_info.get("preco_atual", 0)

        return {
            "ticker": div_info.get("ticker"),
            "cotas": cotas,
            "valor_investido": round(preco_atual * cotas, 2),
            "renda_mensal_estimada": round(media_mensal * cotas, 2),
            "renda_anual_estimada": round(media_mensal * cotas * 12, 2),
            "dividend_yield_anual": div_info.get("dividend_yield_anual", 0)
        }
