"""
Tools para análise de criptoativos e blockchain
Foco em segurança, infraestrutura e gestão de risco
"""
import yfinance as yf
from typing import List, Optional
from datetime import datetime, timedelta


class CriptoTools:
    """Ferramentas para análise técnica e de risco de criptoativos"""

    # Classificação de ativos por risco
    CLASSIFICACAO_ATIVOS = {
        "infraestrutura_base": {
            "BTC": {
                "nome": "Bitcoin",
                "ticker": "BTC-USD",
                "descricao": "Reserva de valor digital, rede mais segura e descentralizada",
                "caso_uso": "Store of value, settlement layer",
                "maturidade": "15+ anos, battle-tested",
                "risco": "VERDE"
            },
            "ETH": {
                "nome": "Ethereum",
                "ticker": "ETH-USD",
                "descricao": "Plataforma de contratos inteligentes, base do DeFi",
                "caso_uso": "Smart contracts, DeFi, NFTs",
                "maturidade": "9+ anos, transição para PoS concluída",
                "risco": "VERDE"
            }
        },
        "infraestrutura_expansao": {
            "SOL": {
                "nome": "Solana",
                "ticker": "SOL-USD",
                "descricao": "L1 de alta performance",
                "caso_uso": "DeFi, NFTs, pagamentos",
                "maturidade": "4+ anos, histórico de outages",
                "risco": "AMARELO"
            },
            "MATIC": {
                "nome": "Polygon",
                "ticker": "MATIC-USD",
                "descricao": "Layer 2 do Ethereum",
                "caso_uso": "Scaling Ethereum, gaming",
                "maturidade": "4+ anos, adoção corporativa",
                "risco": "AMARELO"
            },
            "AVAX": {
                "nome": "Avalanche",
                "ticker": "AVAX-USD",
                "descricao": "L1 com subnets customizáveis",
                "caso_uso": "DeFi, subnets empresariais",
                "maturidade": "4+ anos",
                "risco": "AMARELO"
            },
            "LINK": {
                "nome": "Chainlink",
                "ticker": "LINK-USD",
                "descricao": "Oráculo descentralizado",
                "caso_uso": "Data feeds para smart contracts",
                "maturidade": "6+ anos, infraestrutura crítica do DeFi",
                "risco": "AMARELO"
            }
        },
        "experimental": {
            "descricao": "Projetos novos, não consolidados, alto risco",
            "risco": "VERMELHO",
            "recomendacao": "Máximo 1-2% da carteira cripto"
        },
        "inaceitavel": {
            "descricao": "Meme coins, projetos sem fundamento, promessas irreais",
            "risco": "CAVEIRA",
            "recomendacao": "NUNCA - Zero exposição",
            "exemplos": ["DOGE", "SHIB", "PEPE", "qualquer -INU", "promessas de 1000x"]
        }
    }

    # Limites de exposição recomendados
    LIMITES_EXPOSICAO = {
        "conservador": {
            "cripto_total": 5,
            "btc_minimo": 70,
            "eth_maximo": 25,
            "altcoins_maximo": 5,
            "descricao": "Máximo 5% do patrimônio em cripto, majoritariamente BTC"
        },
        "moderado": {
            "cripto_total": 10,
            "btc_minimo": 50,
            "eth_maximo": 35,
            "altcoins_maximo": 15,
            "descricao": "Até 10% do patrimônio, diversificação controlada"
        },
        "arrojado": {
            "cripto_total": 20,
            "btc_minimo": 40,
            "eth_maximo": 40,
            "altcoins_maximo": 20,
            "descricao": "Até 20% do patrimônio, maior exposição a altcoins sólidas"
        }
    }

    def get_cripto_dados(self, simbolo: str) -> dict:
        """
        Obtém dados atuais de uma criptomoeda.

        Args:
            simbolo: Símbolo da cripto (BTC, ETH, SOL, etc.)

        Returns:
            Dados atuais e métricas
        """
        try:
            ticker = f"{simbolo.upper()}-USD"
            cripto = yf.Ticker(ticker)
            info = cripto.info
            hist = cripto.history(period="1y")

            preco = info.get("regularMarketPrice", info.get("previousClose", 0))

            # Calcular métricas
            variacao_24h = info.get("regularMarketChangePercent", 0)

            # Volatilidade e drawdown
            volatilidade_anual = None
            max_drawdown = None
            variacao_ano = None

            if not hist.empty and len(hist) > 30:
                retornos = hist['Close'].pct_change().dropna()
                volatilidade_anual = retornos.std() * (252 ** 0.5) * 100  # Anualizada

                # Max drawdown
                rolling_max = hist['Close'].cummax()
                drawdown = (hist['Close'] - rolling_max) / rolling_max
                max_drawdown = drawdown.min() * 100

                # Variação no ano
                variacao_ano = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100

            # Classificação de risco
            classificacao = self._classificar_ativo(simbolo.upper())

            return {
                "simbolo": simbolo.upper(),
                "nome": info.get("name", simbolo),
                "preco_usd": round(preco, 2) if preco else "N/A",
                "variacao_24h": f"{variacao_24h:.2f}%" if variacao_24h else "N/A",
                "variacao_12_meses": f"{variacao_ano:.1f}%" if variacao_ano else "N/A",
                "market_cap": info.get("marketCap", "N/A"),
                "volume_24h": info.get("volume24Hr", info.get("volume", "N/A")),
                "metricas_risco": {
                    "volatilidade_anual": f"{volatilidade_anual:.1f}%" if volatilidade_anual else "N/A",
                    "max_drawdown_12m": f"{max_drawdown:.1f}%" if max_drawdown else "N/A"
                },
                "classificacao": classificacao,
                "aviso": "Criptoativos são de alto risco. Nunca invista mais do que pode perder."
            }
        except Exception as e:
            return {"erro": str(e), "simbolo": simbolo}

    def _classificar_ativo(self, simbolo: str) -> dict:
        """Classifica um ativo por categoria de risco."""
        # Verificar infraestrutura base
        if simbolo in self.CLASSIFICACAO_ATIVOS["infraestrutura_base"]:
            info = self.CLASSIFICACAO_ATIVOS["infraestrutura_base"][simbolo]
            return {
                "categoria": "🟢 Infraestrutura Base",
                "risco": "VERDE",
                "descricao": info["descricao"],
                "caso_uso": info["caso_uso"],
                "maturidade": info["maturidade"]
            }

        # Verificar infraestrutura em expansão
        if simbolo in self.CLASSIFICACAO_ATIVOS["infraestrutura_expansao"]:
            info = self.CLASSIFICACAO_ATIVOS["infraestrutura_expansao"][simbolo]
            return {
                "categoria": "🟡 Infraestrutura em Expansão",
                "risco": "AMARELO",
                "descricao": info["descricao"],
                "caso_uso": info["caso_uso"],
                "maturidade": info["maturidade"]
            }

        # Verificar se é meme coin conhecida
        meme_coins = ["DOGE", "SHIB", "PEPE", "FLOKI", "BONK", "WIF", "BRETT"]
        if simbolo in meme_coins:
            return {
                "categoria": "☠️ Inaceitável",
                "risco": "CAVEIRA",
                "descricao": "Meme coin sem fundamento técnico",
                "recomendacao": "ZERO exposição - não é investimento, é aposta"
            }

        # Não classificado = experimental por padrão
        return {
            "categoria": "🔴 Experimental / Não Classificado",
            "risco": "VERMELHO",
            "descricao": "Ativo não avaliado ou de alto risco",
            "recomendacao": "Requer análise aprofundada antes de qualquer exposição"
        }

    def analisar_seguranca_rede(self, simbolo: str) -> dict:
        """
        Analisa aspectos de segurança de uma rede blockchain.

        Args:
            simbolo: Símbolo da cripto

        Returns:
            Análise de segurança
        """
        analises = {
            "BTC": {
                "rede": "Bitcoin",
                "consenso": "Proof of Work",
                "seguranca": {
                    "nivel": "🟢 Máxima",
                    "hashrate": "Maior hashrate do mundo",
                    "descentralizacao": "Alta - milhares de nodes globais",
                    "historico_hacks": "Zero hacks na rede principal",
                    "tempo_ativo": "15+ anos sem downtime"
                },
                "riscos": [
                    "Risco regulatório em alguns países",
                    "Consumo energético (questão ESG)",
                    "Volatilidade de preço"
                ],
                "auditorias": "Código aberto, revisado globalmente por 15 anos",
                "veredicto": "Rede mais segura e testada do ecossistema cripto"
            },
            "ETH": {
                "rede": "Ethereum",
                "consenso": "Proof of Stake",
                "seguranca": {
                    "nivel": "🟢 Alta",
                    "staking": "Milhões de ETH em stake",
                    "descentralizacao": "Alta - milhares de validadores",
                    "historico_hacks": "Rede principal segura (DAO hack foi em smart contract)",
                    "tempo_ativo": "9+ anos, transição PoS bem-sucedida"
                },
                "riscos": [
                    "Complexidade do ecossistema",
                    "Smart contracts podem ter bugs",
                    "Taxas altas em picos de uso",
                    "Risco regulatório (staking)"
                ],
                "auditorias": "Código aberto, múltiplas auditorias, bug bounties ativos",
                "veredicto": "Infraestrutura sólida, mas requer atenção aos protocolos DeFi"
            },
            "SOL": {
                "rede": "Solana",
                "consenso": "Proof of History + Proof of Stake",
                "seguranca": {
                    "nivel": "🟡 Média",
                    "performance": "Alta velocidade, baixas taxas",
                    "descentralizacao": "Média - hardware requirements altos",
                    "historico_hacks": "Múltiplos outages (rede parou)",
                    "tempo_ativo": "4+ anos"
                },
                "riscos": [
                    "Histórico de instabilidade (outages)",
                    "Centralização de validadores",
                    "Dependência de hardware específico",
                    "Menor battle-testing"
                ],
                "auditorias": "Código aberto, auditorias em andamento",
                "veredicto": "Promissor mas ainda provando resiliência"
            }
        }

        simbolo_upper = simbolo.upper()
        if simbolo_upper in analises:
            return analises[simbolo_upper]

        return {
            "rede": simbolo_upper,
            "seguranca": {
                "nivel": "⚠️ Não Avaliada",
                "descricao": "Esta rede não foi analisada em profundidade"
            },
            "recomendacao": "Antes de investir, verifique: auditorias, tempo de operação, histórico de falhas, descentralização",
            "aviso": "Redes não avaliadas devem ser tratadas como alto risco"
        }

    def calcular_exposicao_recomendada(
        self,
        patrimonio_total: float,
        perfil: str = "moderado"
    ) -> dict:
        """
        Calcula exposição máxima recomendada a criptoativos.

        Args:
            patrimonio_total: Patrimônio total do investidor
            perfil: conservador, moderado ou arrojado

        Returns:
            Recomendação de alocação
        """
        perfil_lower = perfil.lower()
        if perfil_lower not in self.LIMITES_EXPOSICAO:
            perfil_lower = "moderado"

        limites = self.LIMITES_EXPOSICAO[perfil_lower]

        exposicao_total = patrimonio_total * (limites["cripto_total"] / 100)
        alocacao_btc = exposicao_total * (limites["btc_minimo"] / 100)
        alocacao_eth = exposicao_total * (limites["eth_maximo"] / 100)
        alocacao_alt = exposicao_total * (limites["altcoins_maximo"] / 100)

        return {
            "perfil": perfil_lower,
            "patrimonio_total": patrimonio_total,
            "exposicao_cripto": {
                "percentual_maximo": f"{limites['cripto_total']}%",
                "valor_maximo": round(exposicao_total, 2),
                "descricao": limites["descricao"]
            },
            "alocacao_sugerida": {
                "bitcoin": {
                    "percentual": f"Mínimo {limites['btc_minimo']}% da carteira cripto",
                    "valor": round(alocacao_btc, 2),
                    "racional": "Base da carteira, maior segurança"
                },
                "ethereum": {
                    "percentual": f"Até {limites['eth_maximo']}% da carteira cripto",
                    "valor": round(alocacao_eth, 2),
                    "racional": "Exposição a smart contracts e DeFi"
                },
                "altcoins_solidas": {
                    "percentual": f"Máximo {limites['altcoins_maximo']}% da carteira cripto",
                    "valor": round(alocacao_alt, 2),
                    "racional": "Apenas projetos 🟡 ou superiores, nunca ☠️"
                }
            },
            "regras_gizmoduck": [
                "Reserva de emergência é INTOCÁVEL - nunca usar para cripto",
                "Nunca alavancagem em cripto",
                "Meme coins = ZERO exposição",
                "DCA (aportes regulares) > timing de mercado",
                "Self-custody para valores relevantes"
            ]
        }

    def avaliar_protocolo_defi(self, protocolo: str) -> dict:
        """
        Avalia riscos de um protocolo DeFi.

        Args:
            protocolo: Nome do protocolo

        Returns:
            Avaliação de risco
        """
        protocolos_avaliados = {
            "AAVE": {
                "nome": "Aave",
                "tipo": "Lending/Borrowing",
                "seguranca": "🟢 Alta",
                "tvl": "Top 5 DeFi",
                "auditorias": "Múltiplas auditorias (OpenZeppelin, Trail of Bits)",
                "historico": "Operando desde 2020, sem hacks significativos",
                "riscos": ["Smart contract risk", "Riscos de liquidação", "Risco regulatório"],
                "veredicto": "Protocolo maduro, um dos mais seguros do DeFi"
            },
            "UNISWAP": {
                "nome": "Uniswap",
                "tipo": "DEX (Exchange Descentralizada)",
                "seguranca": "🟢 Alta",
                "tvl": "Maior DEX por volume",
                "auditorias": "Múltiplas auditorias",
                "historico": "Operando desde 2018, pioneiro em AMM",
                "riscos": ["Impermanent loss para LPs", "Front-running", "Smart contract risk"],
                "veredicto": "DEX mais battle-tested do mercado"
            },
            "LIDO": {
                "nome": "Lido",
                "tipo": "Liquid Staking",
                "seguranca": "🟡 Média-Alta",
                "tvl": "Maior protocolo de liquid staking",
                "auditorias": "Múltiplas auditorias",
                "historico": "Operando desde 2020",
                "riscos": ["Centralização do staking ETH", "Smart contract risk", "Slashing risk"],
                "veredicto": "Líder do setor, mas atenção à concentração"
            }
        }

        protocolo_upper = protocolo.upper()
        if protocolo_upper in protocolos_avaliados:
            return protocolos_avaliados[protocolo_upper]

        return {
            "protocolo": protocolo,
            "avaliacao": "⚠️ Não Avaliado",
            "checklist_antes_de_usar": [
                "Verificar se foi auditado (e por quem)",
                "Tempo de operação sem incidentes",
                "TVL (Total Value Locked) - maior = mais testado",
                "Código é open source?",
                "Equipe é conhecida (doxxed)?",
                "Tem bug bounty ativo?",
                "Comunidade ativa e desenvolvedores ativos?"
            ],
            "aviso": "Protocolos não avaliados devem ser tratados como ALTO RISCO"
        }

    def comparar_custodia(self) -> dict:
        """
        Compara opções de custódia de criptoativos.

        Returns:
            Comparativo de custódia
        """
        return {
            "self_custody": {
                "tipo": "Você guarda suas próprias chaves",
                "opcoes": ["Hardware wallet (Ledger, Trezor)", "Software wallet (MetaMask, etc.)"],
                "vantagens": [
                    "Controle total dos ativos",
                    "Sem risco de exchange quebrar",
                    "Privacidade",
                    "'Not your keys, not your coins'"
                ],
                "desvantagens": [
                    "Responsabilidade total (perder seed = perder tudo)",
                    "Requer conhecimento técnico",
                    "Menos conveniente para trading"
                ],
                "recomendado_para": "Valores acima de R$ 10.000 ou hodlers de longo prazo",
                "seguranca": "🟢 Máxima (se feito corretamente)"
            },
            "exchange_custodia": {
                "tipo": "Exchange guarda seus ativos",
                "opcoes": ["Exchanges grandes (Binance, Coinbase, Kraken)", "Exchanges brasileiras (Mercado Bitcoin, etc.)"],
                "vantagens": [
                    "Conveniente",
                    "Fácil para iniciantes",
                    "Suporte ao cliente",
                    "Seguro de custódia (algumas)"
                ],
                "desvantagens": [
                    "Risco de falência da exchange (FTX, Mt. Gox)",
                    "Hacks são possíveis",
                    "Você não controla as chaves",
                    "KYC obrigatório"
                ],
                "recomendado_para": "Valores menores ou traders ativos",
                "seguranca": "🟡 Média (depende da exchange)"
            },
            "custodia_institucional": {
                "tipo": "Custodiante regulado",
                "opcoes": ["Fireblocks", "BitGo", "Fidelity Digital Assets"],
                "recomendado_para": "Investidores institucionais ou patrimônio muito alto",
                "seguranca": "🟢 Alta (regulado e segurado)"
            },
            "regra_gizmoduck": "Para valores relevantes: SEMPRE self-custody com hardware wallet. Exchanges são para comprar, não para guardar."
        }

    def listar_classificacao_ativos(self) -> dict:
        """
        Lista a classificação completa de ativos por categoria de risco.

        Returns:
            Classificação de todos os ativos
        """
        return {
            "🟢 Infraestrutura Base": {
                "descricao": "Ativos maduros, battle-tested, casos de uso comprovados",
                "exposicao_recomendada": "Base da carteira cripto (70%+)",
                "ativos": self.CLASSIFICACAO_ATIVOS["infraestrutura_base"]
            },
            "🟡 Infraestrutura em Expansão": {
                "descricao": "Projetos sólidos em desenvolvimento, maior risco que a base",
                "exposicao_recomendada": "Complemento da carteira (até 25%)",
                "ativos": self.CLASSIFICACAO_ATIVOS["infraestrutura_expansao"]
            },
            "🔴 Experimental": {
                "descricao": "Projetos novos, não consolidados, alto risco",
                "exposicao_recomendada": "Máximo 5% da carteira cripto",
                "criterios": "Requer análise profunda antes de qualquer exposição"
            },
            "☠️ Inaceitável": {
                "descricao": "Meme coins, projetos sem fundamento, promessas irreais",
                "exposicao_recomendada": "ZERO - Não é investimento",
                "exemplos": self.CLASSIFICACAO_ATIVOS["inaceitavel"]["exemplos"]
            },
            "filosofia_gizmoduck": "Cripto é infraestrutura financeira, não cassino. Segurança > Hype."
        }
