"""
Tools para análise de extratos de cartões de crédito
Classificação, detecção de padrões e alertas inteligentes
"""
import os
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict

# Tentar importar bibliotecas opcionais
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


class CartoesTools:
    """Ferramentas para análise de extratos de cartões de crédito"""

    # Categorias e palavras-chave para classificação automática
    CATEGORIAS = {
        "alimentacao": {
            "keywords": ["ifood", "uber eats", "rappi", "zé delivery", "restaurante", "lanchonete",
                        "padaria", "supermercado", "mercado", "hortifruti", "açougue", "pão de açucar",
                        "carrefour", "extra", "atacadão", "assai", "burger", "pizza", "sushi",
                        "mcdonald", "subway", "starbucks", "outback", "madero"],
            "emoji": "🍽️"
        },
        "transporte": {
            "keywords": ["uber", "99", "cabify", "posto", "shell", "ipiranga", "br distribuidora",
                        "estacionamento", "parking", "pedagio", "sem parar", "conectcar", "move mais",
                        "metrô", "cptm", "bilhete", "recarga transporte"],
            "emoji": "🚗"
        },
        "moradia": {
            "keywords": ["aluguel", "condominio", "iptu", "luz", "energia", "enel", "cpfl", "cemig",
                        "água", "sabesp", "copasa", "gás", "comgás", "naturgy", "internet", "vivo",
                        "claro", "tim", "oi", "net", "sky"],
            "emoji": "🏠"
        },
        "assinaturas": {
            "keywords": ["netflix", "spotify", "amazon prime", "disney", "hbo", "globoplay", "deezer",
                        "apple", "google", "microsoft", "adobe", "dropbox", "icloud", "youtube premium",
                        "twitch", "crunchyroll", "paramount", "star+", "gympass", "totalpass"],
            "emoji": "📱"
        },
        "saude": {
            "keywords": ["farmacia", "drogaria", "droga", "drogasil", "pacheco", "araújo", "pague menos",
                        "hospital", "clinica", "laboratorio", "médico", "consulta", "exame", "plano saude",
                        "unimed", "amil", "bradesco saude", "sulamerica", "academia", "smart fit"],
            "emoji": "💊"
        },
        "educacao": {
            "keywords": ["escola", "faculdade", "universidade", "curso", "udemy", "coursera", "alura",
                        "descomplica", "estrategia", "livro", "livraria", "amazon books", "kindle"],
            "emoji": "📚"
        },
        "lazer": {
            "keywords": ["cinema", "cinemark", "uci", "kinoplex", "teatro", "show", "ingresso", "sympla",
                        "eventim", "ticketmaster", "parque", "viagem", "hotel", "airbnb", "booking",
                        "decolar", "latam", "gol", "azul", "cvc", "hurb"],
            "emoji": "🎬"
        },
        "compras": {
            "keywords": ["amazon", "mercado livre", "magalu", "magazine luiza", "americanas", "shopee",
                        "shein", "aliexpress", "casas bahia", "renner", "riachuelo", "c&a", "zara",
                        "centauro", "netshoes", "nike", "adidas"],
            "emoji": "🛒"
        },
        "servicos_financeiros": {
            "keywords": ["anuidade", "tarifa", "iof", "juros", "multa", "encargos", "seguro cartao",
                        "protecao", "saque", "transferencia"],
            "emoji": "🏦"
        }
    }

    # Assinaturas conhecidas com valores típicos
    ASSINATURAS_CONHECIDAS = {
        "netflix": {"nome": "Netflix", "valor_tipico": (22.90, 55.90)},
        "spotify": {"nome": "Spotify", "valor_tipico": (21.90, 34.90)},
        "amazon prime": {"nome": "Amazon Prime", "valor_tipico": (14.90, 19.90)},
        "disney": {"nome": "Disney+", "valor_tipico": (27.90, 43.90)},
        "hbo max": {"nome": "HBO Max", "valor_tipico": (19.90, 34.90)},
        "youtube premium": {"nome": "YouTube Premium", "valor_tipico": (24.90, 45.90)},
        "apple": {"nome": "Apple (iCloud/Music/TV)", "valor_tipico": (3.50, 37.90)},
        "google one": {"nome": "Google One", "valor_tipico": (6.99, 34.99)},
        "gympass": {"nome": "Gympass", "valor_tipico": (49.90, 249.90)},
        "smart fit": {"nome": "Smart Fit", "valor_tipico": (99.90, 149.90)},
    }

    def __init__(self):
        self.transacoes = []
        self.gastos_por_categoria = defaultdict(float)

    def classificar_transacao(self, descricao: str, valor: float) -> dict:
        """
        Classifica uma transação em categoria baseada na descrição.

        Args:
            descricao: Descrição da transação no extrato
            valor: Valor da transação

        Returns:
            Dicionário com classificação
        """
        descricao_lower = descricao.lower()

        for categoria, info in self.CATEGORIAS.items():
            for keyword in info["keywords"]:
                if keyword in descricao_lower:
                    return {
                        "descricao": descricao,
                        "valor": valor,
                        "categoria": categoria,
                        "emoji": info["emoji"],
                        "confianca": "alta"
                    }

        # Se não encontrou, tenta classificação genérica
        return {
            "descricao": descricao,
            "valor": valor,
            "categoria": "outros",
            "emoji": "❓",
            "confianca": "baixa"
        }

    def analisar_extrato_manual(self, transacoes: List[Dict]) -> dict:
        """
        Analisa uma lista de transações fornecidas manualmente.

        Args:
            transacoes: Lista de dicts com 'descricao' e 'valor'
                       Ex: [{"descricao": "IFOOD", "valor": 45.90}, ...]

        Returns:
            Análise completa do extrato
        """
        if not transacoes:
            return {"erro": "Nenhuma transação fornecida"}

        # Classificar todas as transações
        classificadas = []
        gastos_categoria = defaultdict(float)
        total = 0

        for t in transacoes:
            desc = t.get("descricao", "")
            valor = float(t.get("valor", 0))

            classificacao = self.classificar_transacao(desc, valor)
            classificadas.append(classificacao)

            gastos_categoria[classificacao["categoria"]] += valor
            total += valor

        # Ordenar categorias por valor
        categorias_ordenadas = sorted(
            gastos_categoria.items(),
            key=lambda x: x[1],
            reverse=True
        )

        # Calcular percentuais
        resumo_categorias = []
        for cat, valor in categorias_ordenadas:
            emoji = self.CATEGORIAS.get(cat, {}).get("emoji", "❓")
            percentual = (valor / total * 100) if total > 0 else 0
            resumo_categorias.append({
                "categoria": f"{emoji} {cat.replace('_', ' ').title()}",
                "valor": round(valor, 2),
                "percentual": f"{percentual:.1f}%"
            })

        return {
            "total_gastos": round(total, 2),
            "num_transacoes": len(transacoes),
            "ticket_medio": round(total / len(transacoes), 2) if transacoes else 0,
            "resumo_por_categoria": resumo_categorias,
            "transacoes_classificadas": classificadas[:20],  # Limitar para não sobrecarregar
            "observacao": "Análise baseada em palavras-chave. Revise categorias marcadas com baixa confiança."
        }

    def detectar_assinaturas(self, transacoes: List[Dict]) -> dict:
        """
        Detecta possíveis assinaturas/cobranças recorrentes.

        Args:
            transacoes: Lista de transações

        Returns:
            Lista de possíveis assinaturas encontradas
        """
        assinaturas_encontradas = []
        possiveis_recorrentes = defaultdict(list)

        for t in transacoes:
            desc = t.get("descricao", "").lower()
            valor = float(t.get("valor", 0))

            # Verificar assinaturas conhecidas
            for key, info in self.ASSINATURAS_CONHECIDAS.items():
                if key in desc:
                    assinaturas_encontradas.append({
                        "servico": info["nome"],
                        "valor": valor,
                        "valor_tipico": f"R$ {info['valor_tipico'][0]} - R$ {info['valor_tipico'][1]}",
                        "status": "✅ Valor normal" if info['valor_tipico'][0] <= valor <= info['valor_tipico'][1] else "⚠️ Valor diferente do típico"
                    })
                    break
            else:
                # Agrupar por descrição similar para detectar recorrências
                # Simplifica a descrição para agrupamento
                desc_simplificada = re.sub(r'\d+', '', desc)[:30]
                possiveis_recorrentes[desc_simplificada].append(valor)

        # Identificar possíveis recorrências (mesmo valor ou descrição repetida)
        recorrencias_suspeitas = []
        for desc, valores in possiveis_recorrentes.items():
            if len(valores) >= 2:
                recorrencias_suspeitas.append({
                    "descricao": desc.strip(),
                    "ocorrencias": len(valores),
                    "valores": valores[:5],
                    "possivel_assinatura": len(set(valores)) == 1
                })

        return {
            "assinaturas_identificadas": assinaturas_encontradas,
            "total_assinaturas": round(sum(a["valor"] for a in assinaturas_encontradas), 2),
            "possiveis_recorrencias": recorrencias_suspeitas[:10],
            "dica": "Revise assinaturas que você não usa mais. Pequenos valores mensais somam ao longo do ano!"
        }

    def detectar_anomalias(self, transacoes: List[Dict]) -> dict:
        """
        Detecta possíveis anomalias e cobranças suspeitas.

        Args:
            transacoes: Lista de transações

        Returns:
            Lista de anomalias encontradas
        """
        alertas = []

        # Agrupar transações por descrição para encontrar duplicatas
        por_descricao = defaultdict(list)
        valores = []

        for t in transacoes:
            desc = t.get("descricao", "")
            valor = float(t.get("valor", 0))
            valores.append(valor)
            por_descricao[desc.lower()].append(valor)

        # Calcular média e desvio para detectar outliers
        if valores:
            media = sum(valores) / len(valores)
            # Outliers: valores muito acima da média
            for t in transacoes:
                valor = float(t.get("valor", 0))
                if valor > media * 3 and valor > 500:  # 3x a média e acima de R$ 500
                    alertas.append({
                        "tipo": "🔴 Valor Alto",
                        "descricao": t.get("descricao"),
                        "valor": valor,
                        "motivo": f"Valor {valor/media:.1f}x acima da média do extrato"
                    })

        # Detectar possíveis duplicatas
        for desc, vals in por_descricao.items():
            if len(vals) >= 2:
                # Mesma descrição e mesmo valor = possível duplicata
                valor_counts = defaultdict(int)
                for v in vals:
                    valor_counts[v] += 1

                for v, count in valor_counts.items():
                    if count >= 2:
                        alertas.append({
                            "tipo": "⚠️ Possível Duplicata",
                            "descricao": desc,
                            "valor": v,
                            "ocorrencias": count,
                            "motivo": "Mesma descrição e valor aparece múltiplas vezes"
                        })

        # Detectar cobranças de serviços financeiros (taxas, juros)
        for t in transacoes:
            desc = t.get("descricao", "").lower()
            valor = float(t.get("valor", 0))

            if any(word in desc for word in ["juros", "multa", "encargo", "iof", "tarifa"]):
                alertas.append({
                    "tipo": "💰 Taxa/Encargo",
                    "descricao": t.get("descricao"),
                    "valor": valor,
                    "motivo": "Cobrança de serviço financeiro identificada"
                })

        return {
            "alertas": alertas,
            "total_alertas": len(alertas),
            "recomendacao": "Verifique os alertas e contate o banco se identificar cobranças indevidas"
        }

    def analisar_uso_limite(
        self,
        limite_total: float,
        fatura_atual: float,
        parcelamentos_futuros: float = 0
    ) -> dict:
        """
        Analisa o uso do limite do cartão.

        Args:
            limite_total: Limite total do cartão
            fatura_atual: Valor da fatura atual
            parcelamentos_futuros: Soma de parcelas futuras já comprometidas

        Returns:
            Análise de uso do limite
        """
        if limite_total <= 0:
            return {"erro": "Limite deve ser maior que zero"}

        uso_atual = (fatura_atual / limite_total) * 100
        comprometido_total = fatura_atual + parcelamentos_futuros
        uso_comprometido = (comprometido_total / limite_total) * 100
        disponivel = limite_total - comprometido_total

        # Classificar saúde do uso
        if uso_atual <= 30:
            status = "🟢 Saudável"
            mensagem = "Excelente! Uso controlado do cartão."
        elif uso_atual <= 50:
            status = "🟡 Atenção"
            mensagem = "Uso moderado. Ideal manter abaixo de 30%."
        elif uso_atual <= 70:
            status = "🟠 Alerta"
            mensagem = "Uso elevado. Considere reduzir gastos no cartão."
        else:
            status = "🔴 Crítico"
            mensagem = "Uso muito alto! Risco de endividamento."

        return {
            "limite_total": limite_total,
            "fatura_atual": fatura_atual,
            "parcelamentos_futuros": parcelamentos_futuros,
            "total_comprometido": round(comprometido_total, 2),
            "disponivel_real": round(max(0, disponivel), 2),
            "uso_percentual": f"{uso_atual:.1f}%",
            "uso_comprometido_percentual": f"{uso_comprometido:.1f}%",
            "status": status,
            "mensagem": mensagem,
            "recomendacoes": [
                "Ideal: usar até 30% do limite",
                "Pague sempre o valor total da fatura",
                "Evite parcelar compras do dia-a-dia",
                "Rotativo do cartão tem os maiores juros do mercado"
            ]
        }

    def simular_parcelamento(
        self,
        valor_total: float,
        num_parcelas: int,
        taxa_juros_mensal: float = 0
    ) -> dict:
        """
        Simula um parcelamento no cartão.

        Args:
            valor_total: Valor total da compra
            num_parcelas: Número de parcelas
            taxa_juros_mensal: Taxa de juros mensal (0 = sem juros)

        Returns:
            Simulação do parcelamento
        """
        if taxa_juros_mensal > 0:
            # Com juros (Price)
            taxa = taxa_juros_mensal / 100
            parcela = valor_total * (taxa * (1 + taxa)**num_parcelas) / ((1 + taxa)**num_parcelas - 1)
            total_pago = parcela * num_parcelas
            juros_total = total_pago - valor_total
        else:
            # Sem juros
            parcela = valor_total / num_parcelas
            total_pago = valor_total
            juros_total = 0

        return {
            "valor_compra": valor_total,
            "num_parcelas": num_parcelas,
            "taxa_juros": f"{taxa_juros_mensal}% a.m." if taxa_juros_mensal > 0 else "Sem juros",
            "valor_parcela": round(parcela, 2),
            "total_a_pagar": round(total_pago, 2),
            "juros_total": round(juros_total, 2),
            "custo_adicional_percentual": f"{(juros_total/valor_total)*100:.1f}%" if valor_total > 0 else "0%",
            "impacto_limite": f"Compromete R$ {round(parcela, 2)}/mês por {num_parcelas} meses",
            "dica": "Parcelamentos sem juros são interessantes se você teria o dinheiro guardado rendendo. Com juros, evite!"
        }

    def gerar_relatorio_mensal(
        self,
        transacoes: List[Dict],
        limite_cartao: float = None,
        mes_anterior: Dict = None
    ) -> dict:
        """
        Gera um relatório mensal completo do cartão.

        Args:
            transacoes: Lista de transações do mês
            limite_cartao: Limite total do cartão (opcional)
            mes_anterior: Dados do mês anterior para comparação (opcional)

        Returns:
            Relatório mensal completo
        """
        # Análise básica
        analise = self.analisar_extrato_manual(transacoes)
        assinaturas = self.detectar_assinaturas(transacoes)
        anomalias = self.detectar_anomalias(transacoes)

        relatorio = {
            "periodo": "Mensal",
            "resumo": {
                "total_gastos": analise["total_gastos"],
                "num_transacoes": analise["num_transacoes"],
                "ticket_medio": analise["ticket_medio"]
            },
            "categorias": analise["resumo_por_categoria"],
            "assinaturas": {
                "total": assinaturas["total_assinaturas"],
                "servicos": assinaturas["assinaturas_identificadas"]
            },
            "alertas": anomalias["alertas"]
        }

        # Análise de limite se fornecido
        if limite_cartao:
            uso_limite = self.analisar_uso_limite(limite_cartao, analise["total_gastos"])
            relatorio["uso_limite"] = uso_limite

        # Comparação com mês anterior se fornecido
        if mes_anterior and "total_gastos" in mes_anterior:
            variacao = analise["total_gastos"] - mes_anterior["total_gastos"]
            variacao_perc = (variacao / mes_anterior["total_gastos"]) * 100 if mes_anterior["total_gastos"] > 0 else 0

            relatorio["comparativo"] = {
                "mes_anterior": mes_anterior["total_gastos"],
                "mes_atual": analise["total_gastos"],
                "variacao": round(variacao, 2),
                "variacao_percentual": f"{variacao_perc:+.1f}%",
                "tendencia": "📈 Aumento" if variacao > 0 else "📉 Redução" if variacao < 0 else "➡️ Estável"
            }

        # Insights da Webby
        insights = []

        # Top categoria
        if analise["resumo_por_categoria"]:
            top = analise["resumo_por_categoria"][0]
            insights.append(f"Maior gasto: {top['categoria']} ({top['percentual']} do total)")

        # Assinaturas
        if assinaturas["total_assinaturas"] > 0:
            insights.append(f"Assinaturas identificadas: R$ {assinaturas['total_assinaturas']}/mês")

        # Alertas
        if anomalias["total_alertas"] > 0:
            insights.append(f"⚠️ {anomalias['total_alertas']} alerta(s) requerem sua atenção")

        # Uso do limite
        if limite_cartao and analise["total_gastos"] / limite_cartao > 0.5:
            insights.append("🔴 Uso do limite acima de 50% - considere reduzir gastos")

        relatorio["insights_webby"] = insights

        return relatorio

    def listar_categorias(self) -> dict:
        """
        Lista todas as categorias disponíveis para classificação.

        Returns:
            Lista de categorias com exemplos
        """
        categorias = []
        for nome, info in self.CATEGORIAS.items():
            categorias.append({
                "categoria": f"{info['emoji']} {nome.replace('_', ' ').title()}",
                "exemplos": info["keywords"][:5]
            })

        return {
            "categorias_disponiveis": categorias,
            "total_categorias": len(categorias),
            "nota": "Transações não reconhecidas são classificadas como 'Outros'"
        }
