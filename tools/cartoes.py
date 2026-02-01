"""
Tools para análise de extratos de cartões de crédito
Classificação, detecção de padrões e alertas inteligentes
Integração com Gmail/Drive/Sheets para extratos CSV Nubank
"""
import os
import io
import csv
import re
import base64
from typing import List, Dict, Optional, TypedDict
from datetime import datetime, timedelta


class Transacao(TypedDict, total=False):
    descricao: str
    valor: float
    data: str


from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

# Tentar importar bibliotecas opcionais
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_APIS_AVAILABLE = True
except ImportError:
    GOOGLE_APIS_AVAILABLE = False

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/drive.metadata',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]


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
        self._gmail_service = None
        self._drive_service = None
        self._sheets_service = None
        self._credentials = None

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

    def analisar_extrato_manual(self, transacoes: List[Transacao]) -> dict:
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

    def detectar_assinaturas(self, transacoes: List[Transacao]) -> dict:
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

    def detectar_anomalias(self, transacoes: List[Transacao]) -> dict:
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
        transacoes: List[Transacao],
        limite_cartao: float = None,
        mes_anterior: Optional[dict] = None
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

    # ===== Integração Gmail/Drive/Sheets para extratos CSV Nubank =====

    def _get_credentials(self) -> Optional['Credentials']:
        """Obtém ou atualiza credenciais OAuth do Google"""
        if not GOOGLE_APIS_AVAILABLE:
            return None

        if self._credentials and self._credentials.valid:
            return self._credentials

        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self._credentials = creds
        return creds

    def _get_gmail(self):
        """Retorna serviço Gmail (lazy-load)"""
        if not self._gmail_service:
            creds = self._get_credentials()
            if creds:
                self._gmail_service = build('gmail', 'v1', credentials=creds)
        return self._gmail_service

    def _get_drive(self):
        """Retorna serviço Drive (lazy-load)"""
        if not self._drive_service:
            creds = self._get_credentials()
            if creds:
                self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service

    def _get_sheets(self):
        """Retorna serviço Sheets (lazy-load)"""
        if not self._sheets_service:
            creds = self._get_credentials()
            if creds:
                self._sheets_service = build('sheets', 'v4', credentials=creds)
        return self._sheets_service

    def _extrair_transacoes_csv(self, file_content: bytes) -> List[Dict]:
        """
        Extrai transações de um CSV de extrato Nubank.

        O CSV do Nubank tem colunas: date,category,title,amount
        Exemplo:
            date,category,title,amount
            2025-01-15,restaurante,IFOOD *IFOOD,-45.90
            2025-01-16,transporte,Uber *Trip,-22.50

        Args:
            file_content: Conteúdo do CSV em bytes

        Returns:
            Lista de dicts com 'data', 'descricao', 'valor', 'categoria_nubank'
        """
        transacoes = []
        try:
            # Tentar decodificar com utf-8, fallback para latin-1
            try:
                text = file_content.decode('utf-8')
            except UnicodeDecodeError:
                text = file_content.decode('latin-1')

            reader = csv.DictReader(io.StringIO(text))

            for row in reader:
                # Colunas padrão Nubank CSV: date, category, title, amount
                data = row.get('date', '').strip()
                categoria_nu = row.get('category', '').strip()
                descricao = row.get('title', '').strip()
                valor_str = row.get('amount', '0').strip()

                if not descricao or not valor_str:
                    continue

                try:
                    valor = abs(float(valor_str.replace(',', '.')))
                except ValueError:
                    continue

                transacoes.append({
                    "data": data,
                    "descricao": descricao,
                    "valor": valor,
                    "categoria_nubank": categoria_nu
                })

        except Exception:
            pass

        return transacoes

    def _registrar_na_planilha(self, transacoes_classificadas: List[Dict], mes_ref: str) -> dict:
        """
        Registra transações classificadas na planilha Google Sheets.

        Cria/usa aba com nome do mês (ex: "2025-01") e grava:
        Data | Descrição | Valor | Categoria | Categoria Nubank

        Args:
            transacoes_classificadas: Lista de transações já classificadas
            mes_ref: Mês de referência no formato "YYYY-MM"

        Returns:
            Resultado da gravação
        """
        sheets = self._get_sheets()
        if not sheets:
            return {"erro": "Serviço Sheets não disponível"}

        sheets_id = os.getenv("CARTOES_SHEETS_ID")
        if not sheets_id:
            return {"erro": "CARTOES_SHEETS_ID não configurado no .env"}

        aba = f"Cartão {mes_ref}"

        try:
            # Verificar se aba existe, senão criar
            spreadsheet = sheets.spreadsheets().get(
                spreadsheetId=sheets_id
            ).execute()

            abas_existentes = [s['properties']['title'] for s in spreadsheet.get('sheets', [])]

            if aba not in abas_existentes:
                sheets.spreadsheets().batchUpdate(
                    spreadsheetId=sheets_id,
                    body={
                        "requests": [{
                            "addSheet": {
                                "properties": {"title": aba}
                            }
                        }]
                    }
                ).execute()

                # Escrever cabeçalho
                sheets.spreadsheets().values().update(
                    spreadsheetId=sheets_id,
                    range=f"'{aba}'!A1:E1",
                    valueInputOption="USER_ENTERED",
                    body={"values": [["Data", "Descrição", "Valor", "Categoria", "Categoria Nubank"]]}
                ).execute()

            # Preparar linhas
            rows = []
            for t in transacoes_classificadas:
                rows.append([
                    t.get("data", ""),
                    t.get("descricao", ""),
                    f"{t.get('valor', 0):.2f}".replace('.', ','),
                    t.get("categoria", "outros"),
                    t.get("categoria_nubank", ""),
                ])

            if rows:
                sheets.spreadsheets().values().append(
                    spreadsheetId=sheets_id,
                    range=f"'{aba}'!A2",
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body={"values": rows, "majorDimension": "ROWS"}
                ).execute()

            return {
                "status": "ok",
                "aba": aba,
                "linhas_gravadas": len(rows)
            }

        except Exception as e:
            return {"erro": str(e)}

    def buscar_extratos_nubank(self, apenas_nao_lidos: bool = True, limite: int = 10) -> dict:
        """
        Busca emails da Nubank com extratos CSV anexados no Gmail.

        Args:
            apenas_nao_lidos: Se True, busca apenas emails não lidos
            limite: Número máximo de emails para buscar

        Returns:
            Lista de emails encontrados com informações dos anexos CSV
        """
        if not GOOGLE_APIS_AVAILABLE:
            return {"erro": "Bibliotecas do Google não instaladas. Execute: pip install google-api-python-client google-auth-oauthlib"}

        gmail = self._get_gmail()
        if not gmail:
            return {"erro": "Serviço Gmail não disponível. Verifique credentials.json e token.json"}

        query = "from:todomundo@nubank.com.br has:attachment filename:csv"
        if apenas_nao_lidos:
            query = "is:unread " + query

        try:
            results = gmail.users().messages().list(
                userId='me',
                q=query,
                maxResults=limite
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return {
                    "status": "ok",
                    "total": 0,
                    "mensagem": "Nenhum email da Nubank com CSV encontrado",
                    "emails": []
                }

            emails_info = []
            for message in messages:
                msg = gmail.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                headers = {h['name']: h['value'] for h in msg['payload']['headers']}

                anexos = []
                parts = msg['payload'].get('parts', [])
                for part in parts:
                    filename = part.get('filename', '')
                    if filename and filename.lower().endswith('.csv'):
                        anexos.append({
                            "nome": filename,
                            "attachment_id": part['body'].get('attachmentId')
                        })

                if anexos:
                    emails_info.append({
                        "id": message['id'],
                        "assunto": headers.get('Subject', ''),
                        "data": headers.get('Date', ''),
                        "anexos_csv": anexos
                    })

            return {
                "status": "ok",
                "total": len(emails_info),
                "emails": emails_info
            }

        except Exception as e:
            return {"erro": str(e)}

    def processar_extratos_nubank(self, apenas_nao_lidos: bool = True, limite: int = 10) -> dict:
        """
        Fluxo completo automático para extratos Nubank:
        1. Busca emails da Nubank com CSV anexado no Gmail
        2. Baixa cada CSV
        3. Envia CSV para pasta "Extratos Cartões" no Google Drive
        4. Lê e parseia as transações do CSV
        5. Classifica cada transação por categoria
        6. Grava na planilha Google Sheets (uma aba por mês)
        7. Marca email como lido
        8. Retorna análise completa (categorias, assinaturas, anomalias)

        Args:
            apenas_nao_lidos: Se True, processa apenas emails não lidos
            limite: Número máximo de emails para processar

        Returns:
            Relatório completo com processamento e análise integrada
        """
        if not GOOGLE_APIS_AVAILABLE:
            return {"erro": "Bibliotecas do Google não instaladas"}

        gmail = self._get_gmail()
        drive = self._get_drive()

        if not gmail or not drive:
            return {"erro": "Serviços Gmail/Drive não disponíveis"}

        folder_id = os.getenv("CARTOES_FOLDER_ID")
        if not folder_id:
            return {"erro": "CARTOES_FOLDER_ID não configurado no .env. Defina o ID da pasta 'Extratos Cartões' no Google Drive."}

        query = "from:todomundo@nubank.com.br has:attachment filename:csv"
        if apenas_nao_lidos:
            query = "is:unread " + query

        try:
            results = gmail.users().messages().list(
                userId='me',
                q=query,
                maxResults=limite
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return {
                    "status": "ok",
                    "emails_processados": 0,
                    "csvs_enviados": 0,
                    "transacoes_extraidas": 0,
                    "mensagem": "Nenhum email da Nubank com CSV para processar"
                }

            csvs_enviados = []
            todas_transacoes = []
            emails_processados = 0

            for message in messages:
                msg = gmail.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                assunto = headers.get('Subject', 'Sem assunto')

                parts = msg['payload'].get('parts', [])
                email_tem_csv = False

                for part in parts:
                    filename = part.get('filename', '')
                    if not filename or not filename.lower().endswith('.csv'):
                        continue

                    if not ('body' in part and 'attachmentId' in part['body']):
                        continue

                    # Baixar anexo CSV do Gmail
                    attachment = gmail.users().messages().attachments().get(
                        userId='me',
                        messageId=message['id'],
                        id=part['body']['attachmentId']
                    ).execute()

                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                    # Verificar se já existe no Drive
                    nome_base = filename.rsplit('.', 1)[0]
                    existing = drive.files().list(
                        q=f"'{folder_id}' in parents and name contains '{nome_base}'",
                        fields="files(id, name)"
                    ).execute()

                    if not existing.get('files'):
                        # Upload CSV para o Drive
                        file_metadata = {
                            'name': filename,
                            'mimeType': 'text/csv',
                            'parents': [folder_id]
                        }

                        media = MediaIoBaseUpload(
                            io.BytesIO(file_data),
                            mimetype='text/csv',
                            resumable=True
                        )

                        uploaded = drive.files().create(
                            body=file_metadata,
                            media_body=media,
                            fields='id,name,webViewLink'
                        ).execute()

                        csvs_enviados.append({
                            "nome": uploaded.get('name'),
                            "id": uploaded.get('id'),
                            "link": uploaded.get('webViewLink'),
                            "assunto_email": assunto
                        })

                    # Parsear transações do CSV (sempre, mesmo se já no Drive)
                    transacoes_csv = self._extrair_transacoes_csv(file_data)
                    todas_transacoes.extend(transacoes_csv)

                    email_tem_csv = True

                # Marcar email como lido
                if email_tem_csv:
                    gmail.users().messages().modify(
                        userId='me',
                        id=message['id'],
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()
                    emails_processados += 1

            # === Classificar transações e gerar análise ===
            if not todas_transacoes:
                return {
                    "status": "ok",
                    "emails_processados": emails_processados,
                    "csvs_enviados": len(csvs_enviados),
                    "transacoes_extraidas": 0,
                    "arquivos": csvs_enviados,
                    "mensagem": "CSVs processados mas nenhuma transação extraída. Verifique o formato do CSV."
                }

            # Classificar cada transação
            transacoes_classificadas = []
            for t in todas_transacoes:
                classificacao = self.classificar_transacao(t["descricao"], t["valor"])
                transacoes_classificadas.append({
                    **t,
                    "categoria": classificacao["categoria"],
                    "emoji": classificacao["emoji"],
                    "confianca": classificacao["confianca"],
                })

            # Detectar mês de referência a partir das datas
            meses = set()
            for t in todas_transacoes:
                data = t.get("data", "")
                if len(data) >= 7:  # "YYYY-MM" ou "YYYY-MM-DD"
                    meses.add(data[:7])
            mes_ref = sorted(meses)[-1] if meses else datetime.now().strftime("%Y-%m")

            # Gravar na planilha
            resultado_planilha = self._registrar_na_planilha(transacoes_classificadas, mes_ref)

            # Análises
            analise_extrato = self.analisar_extrato_manual(todas_transacoes)
            analise_assinaturas = self.detectar_assinaturas(todas_transacoes)
            analise_anomalias = self.detectar_anomalias(todas_transacoes)

            return {
                "status": "ok",
                "emails_processados": emails_processados,
                "csvs_enviados": len(csvs_enviados),
                "transacoes_extraidas": len(todas_transacoes),
                "arquivos": csvs_enviados,
                "planilha": resultado_planilha,
                "analise": analise_extrato,
                "assinaturas": analise_assinaturas,
                "anomalias": analise_anomalias,
                "resumo": (
                    f"Processados {emails_processados} email(s) da Nubank. "
                    f"Encontradas {len(todas_transacoes)} transações totalizando R$ {analise_extrato.get('total_gastos', 0):.2f}. "
                    f"Dados gravados na aba '{resultado_planilha.get('aba', mes_ref)}' da planilha. "
                    f"{analise_anomalias.get('total_alertas', 0)} alerta(s) identificado(s)."
                )
            }

        except Exception as e:
            return {"erro": str(e)}
