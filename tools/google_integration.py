"""
Tools de integração com Google (Gmail, Drive, Sheets)
Para processamento de notas de corretagem
"""
import os
import io
import re
import base64
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Imports do Google APIs
try:
    import pdfplumber
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


class GoogleIntegrationTools:
    """Ferramentas para integração com Gmail, Drive e Sheets"""

    def __init__(self):
        self._gmail_service = None
        self._drive_service = None
        self._sheets_service = None
        self._credentials = None

    def _get_credentials(self) -> Optional[Credentials]:
        """Obtém ou atualiza credenciais do Google"""
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
        """Retorna serviço Gmail"""
        if not self._gmail_service:
            creds = self._get_credentials()
            if creds:
                self._gmail_service = build('gmail', 'v1', credentials=creds)
        return self._gmail_service

    def _get_drive(self):
        """Retorna serviço Drive"""
        if not self._drive_service:
            creds = self._get_credentials()
            if creds:
                self._drive_service = build('drive', 'v3', credentials=creds)
        return self._drive_service

    def _get_sheets(self):
        """Retorna serviço Sheets"""
        if not self._sheets_service:
            creds = self._get_credentials()
            if creds:
                self._sheets_service = build('sheets', 'v4', credentials=creds)
        return self._sheets_service

    def verificar_conexao(self) -> dict:
        """
        Verifica se as conexões com Google APIs estão funcionando.

        Returns:
            Status das conexões com Gmail, Drive e Sheets
        """
        if not GOOGLE_APIS_AVAILABLE:
            return {
                "status": "erro",
                "mensagem": "Bibliotecas do Google não instaladas. Execute: pip install google-api-python-client google-auth-oauthlib pdfplumber"
            }

        status = {
            "gmail": False,
            "drive": False,
            "sheets": False,
            "credenciais": os.path.exists('credentials.json'),
            "token": os.path.exists('token.json')
        }

        try:
            if self._get_gmail():
                status["gmail"] = True
            if self._get_drive():
                status["drive"] = True
            if self._get_sheets():
                status["sheets"] = True

            status["status"] = "ok" if all([status["gmail"], status["drive"], status["sheets"]]) else "parcial"
        except Exception as e:
            status["status"] = "erro"
            status["erro"] = str(e)

        return status

    def diagnosticar_emails_rico(self) -> dict:
        """
        Diagnóstico completo para identificar problemas na busca de emails da Rico.
        Testa diferentes queries e mostra o que está encontrando.

        Returns:
            Relatório de diagnóstico
        """
        gmail = self._get_gmail()
        if not gmail:
            return {"erro": "Serviço Gmail não disponível"}

        diagnostico = {
            "status": "ok",
            "testes": []
        }

        # Lista de queries para testar
        queries_teste = [
            ("Todos emails com 'rico' no remetente", "from:rico"),
            ("Emails de no-reply@rico.com.vc", "from:no-reply@rico.com.vc"),
            ("Emails de noreply@rico.com.vc", "from:noreply@rico.com.vc"),
            ("Emails de rico.com.vc (qualquer)", "from:rico.com.vc"),
            ("Emails Rico com anexo", "(from:no-reply@rico.com.vc OR from:noreply@rico.com.vc) has:attachment"),
            ("Emails Rico não lidos com anexo", "is:unread (from:no-reply@rico.com.vc OR from:noreply@rico.com.vc) has:attachment"),
        ]

        try:
            for descricao, query in queries_teste:
                results = gmail.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=5
                ).execute()

                messages = results.get('messages', [])
                total = results.get('resultSizeEstimate', 0)

                teste_info = {
                    "descricao": descricao,
                    "query": query,
                    "encontrados": len(messages),
                    "total_estimado": total
                }

                # Se encontrou, pegar info do primeiro email
                if messages:
                    msg = gmail.users().messages().get(
                        userId='me',
                        id=messages[0]['id'],
                        format='metadata',
                        metadataHeaders=['From', 'Subject', 'Date']
                    ).execute()

                    headers = {h['name']: h['value'] for h in msg.get('payload', {}).get('headers', [])}
                    teste_info["exemplo"] = {
                        "de": headers.get('From', 'N/A'),
                        "assunto": headers.get('Subject', 'N/A'),
                        "data": headers.get('Date', 'N/A')
                    }

                diagnostico["testes"].append(teste_info)

            # Resumo
            diagnostico["resumo"] = {
                "emails_rico_encontrados": any(t["encontrados"] > 0 for t in diagnostico["testes"]),
                "recomendacao": ""
            }

            if not any(t["encontrados"] > 0 for t in diagnostico["testes"]):
                diagnostico["resumo"]["recomendacao"] = "Nenhum email da Rico encontrado. Verifique se você recebe emails de no-reply@rico.com.vc ou noreply@rico.com.vc"
            else:
                # Encontrar qual query funcionou
                for teste in diagnostico["testes"]:
                    if teste["encontrados"] > 0:
                        diagnostico["resumo"]["recomendacao"] = f"Emails encontrados com: {teste['descricao']}"
                        break

        except Exception as e:
            diagnostico["status"] = "erro"
            diagnostico["erro"] = str(e)

        return diagnostico

    def buscar_emails_rico(self, apenas_nao_lidos: bool = True, limite: int = 10) -> dict:
        """
        Busca emails da Rico corretora com anexos PDF.

        Args:
            apenas_nao_lidos: Se True, busca apenas emails não lidos
            limite: Número máximo de emails para buscar

        Returns:
            Lista de emails encontrados com informações dos anexos
        """
        gmail = self._get_gmail()
        if not gmail:
            return {"erro": "Serviço Gmail não disponível"}

        # Buscar de ambos os remetentes possíveis da Rico
        query = "(from:no-reply@rico.com.vc OR from:noreply@rico.com.vc) has:attachment"
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
                    "mensagem": "Nenhum email encontrado",
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
                if 'parts' in msg['payload']:
                    for part in msg['payload']['parts']:
                        if part.get('filename') and part['filename'].lower().endswith('.pdf'):
                            anexos.append({
                                "nome": part['filename'],
                                "attachment_id": part['body'].get('attachmentId')
                            })

                emails_info.append({
                    "id": message['id'],
                    "assunto": headers.get('Subject', ''),
                    "data": headers.get('Date', ''),
                    "anexos_pdf": anexos
                })

            return {
                "status": "ok",
                "total": len(emails_info),
                "emails": emails_info
            }

        except Exception as e:
            return {"erro": str(e)}

    def processar_emails_rico(self, apenas_nao_lidos: bool = False, limite: int = 500) -> dict:
        """
        Processa emails da Rico, extrai PDFs e envia para o Drive.

        Args:
            apenas_nao_lidos: Se True, processa só não lidos. Se False, processa todos.
            limite: Número máximo de emails para processar

        Returns:
            Resultado do processamento com quantidade de arquivos enviados
        """
        gmail = self._get_gmail()
        drive = self._get_drive()

        if not gmail or not drive:
            return {"erro": "Serviços Gmail/Drive não disponíveis"}

        folder_id = os.getenv("FOLDER_ID")
        if not folder_id:
            return {"erro": "FOLDER_ID não configurado no .env"}

        try:
            # Buscar emails - com ou sem filtro de não lidos
            # Busca de ambos os remetentes possíveis da Rico (no-reply e noreply)
            query = "(from:no-reply@rico.com.vc OR from:noreply@rico.com.vc) has:attachment"
            if apenas_nao_lidos:
                query = "is:unread " + query

            # Buscar com paginação para pegar todos
            all_messages = []
            page_token = None

            while len(all_messages) < limite:
                results = gmail.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=min(100, limite - len(all_messages)),
                    pageToken=page_token
                ).execute()

                messages = results.get('messages', [])
                if not messages:
                    break

                all_messages.extend(messages)

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            messages = all_messages

            if not messages:
                return {
                    "status": "ok",
                    "processados": 0,
                    "mensagem": "Nenhum email para processar"
                }

            arquivos_enviados = []
            arquivos_ignorados = []

            for message in messages:
                msg = gmail.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='full'
                ).execute()

                headers = {h['name']: h['value'] for h in msg['payload']['headers']}

                if 'parts' not in msg['payload']:
                    continue

                for part in msg['payload']['parts']:
                    if part.get('filename') and part['filename'].lower().endswith('.pdf'):
                        filename = part['filename']

                        # Verificar se arquivo já existe no Drive
                        existing = drive.files().list(
                            q=f"'{folder_id}' in parents and name contains '{filename.split('.')[0]}'",
                            fields="files(id, name)"
                        ).execute()

                        if existing.get('files'):
                            arquivos_ignorados.append({"nome": filename, "motivo": "já existe no Drive"})
                            continue

                        if 'body' in part and 'attachmentId' in part['body']:
                            attachment_id = part['body']['attachmentId']
                            attachment = gmail.users().messages().attachments().get(
                                userId='me',
                                messageId=message['id'],
                                id=attachment_id
                            ).execute()

                            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                            # Upload para o Drive
                            file_metadata = {
                                'name': filename,
                                'mimeType': 'application/pdf',
                                'parents': [folder_id]
                            }

                            media = MediaIoBaseUpload(
                                io.BytesIO(file_data),
                                mimetype='application/pdf',
                                resumable=True
                            )

                            file = drive.files().create(
                                body=file_metadata,
                                media_body=media,
                                fields='id,name,webViewLink'
                            ).execute()

                            arquivos_enviados.append({
                                "nome": file.get('name'),
                                "id": file.get('id'),
                                "link": file.get('webViewLink')
                            })

                            # Marcar email como lido após enviar PDF com sucesso
                            gmail.users().messages().modify(
                                userId='me',
                                id=message['id'],
                                body={'removeLabelIds': ['UNREAD']}
                            ).execute()

            return {
                "status": "ok",
                "emails_encontrados": len(messages),
                "processados": len(arquivos_enviados),
                "ignorados": len(arquivos_ignorados),
                "arquivos": arquivos_enviados,
                "arquivos_ignorados": arquivos_ignorados
            }

        except Exception as e:
            return {"erro": str(e)}

    def listar_pdfs_drive(self, apenas_nao_processados: bool = True) -> dict:
        """
        Lista arquivos PDF na pasta do Drive.

        Args:
            apenas_nao_processados: Se True, lista apenas PDFs não processados

        Returns:
            Lista de arquivos PDF encontrados
        """
        drive = self._get_drive()
        if not drive:
            return {"erro": "Serviço Drive não disponível"}

        folder_id = os.getenv("FOLDER_ID")
        if not folder_id:
            return {"erro": "FOLDER_ID não configurado no .env"}

        try:
            query = f"'{folder_id}' in parents and mimeType='application/pdf'"
            if apenas_nao_processados:
                query += " and not name contains 'PROCESSADO'"

            results = drive.files().list(
                q=query,
                pageSize=50,
                fields="files(id, name, createdTime, modifiedTime)",
                orderBy="modifiedTime desc"
            ).execute()

            files = results.get('files', [])

            return {
                "status": "ok",
                "total": len(files),
                "arquivos": [
                    {
                        "id": f['id'],
                        "nome": f['name'],
                        "criado": f.get('createdTime'),
                        "modificado": f.get('modifiedTime')
                    }
                    for f in files
                ]
            }

        except Exception as e:
            return {"erro": str(e)}

    def processar_pdfs_drive(self) -> dict:
        """
        Processa PDFs não lidos do Drive, extrai negociações e envia para planilha.

        Returns:
            Resultado do processamento com quantidade de negociações extraídas
        """
        drive = self._get_drive()
        sheets = self._get_sheets()

        if not drive or not sheets:
            return {"erro": "Serviços Drive/Sheets não disponíveis"}

        folder_id = os.getenv("FOLDER_ID")
        sheets_id = os.getenv("SHEETS_ID")

        if not folder_id or not sheets_id:
            return {"erro": "FOLDER_ID ou SHEETS_ID não configurados no .env"}

        try:
            # Buscar PDFs não processados
            query = f"""
            '{folder_id}' in parents and
            mimeType='application/pdf' and
            not name contains 'PROCESSADO'
            """

            results = drive.files().list(
                q=query,
                pageSize=20,
                fields="files(id, name)",
                orderBy="modifiedTime asc"
            ).execute()

            files = results.get('files', [])

            if not files:
                return {
                    "status": "ok",
                    "processados": 0,
                    "mensagem": "Nenhum PDF novo para processar"
                }

            total_negociacoes = 0
            arquivos_processados = []

            for file in files:
                try:
                    # Download do PDF
                    request = drive.files().get_media(fileId=file['id'])
                    file_content = request.execute()

                    # Extrair texto
                    text = self._extract_text_from_pdf(
                        file_content,
                        password=os.getenv("PDF_PASSWORD")
                    )

                    if not text:
                        self._mark_as_processed(drive, file['id'], file['name'], "SEM_TEXTO")
                        continue

                    # Extrair negociações
                    data = self._extract_trades_from_text(text)

                    if not data.get('trades'):
                        self._mark_as_processed(drive, file['id'], file['name'], "SEM_NEGOCIACOES")
                        continue

                    # Enviar para planilha
                    for trade in data['trades']:
                        self._append_to_sheet(sheets, sheets_id, trade)
                        total_negociacoes += 1

                    # Marcar como processado
                    self._mark_as_processed(drive, file['id'], file['name'], "SUCESSO")
                    arquivos_processados.append({
                        "nome": file['name'],
                        "negociacoes": len(data['trades'])
                    })

                except Exception as e:
                    self._mark_as_processed(drive, file['id'], file['name'], "ERRO")
                    continue

            return {
                "status": "ok",
                "arquivos_processados": len(arquivos_processados),
                "total_negociacoes": total_negociacoes,
                "detalhes": arquivos_processados
            }

        except Exception as e:
            return {"erro": str(e)}

    def consultar_planilha(self, aba: str = "Negociações", limite: int = 10) -> dict:
        """
        Consulta dados da planilha de negociações.

        Args:
            aba: Nome da aba a consultar
            limite: Número máximo de linhas para retornar

        Returns:
            Dados da planilha
        """
        sheets = self._get_sheets()
        if not sheets:
            return {"erro": "Serviço Sheets não disponível"}

        sheets_id = os.getenv("SHEETS_ID")
        if not sheets_id:
            return {"erro": "SHEETS_ID não configurado no .env"}

        try:
            result = sheets.spreadsheets().values().get(
                spreadsheetId=sheets_id,
                range=f"{aba}!A1:F{limite + 1}"
            ).execute()

            values = result.get('values', [])

            if not values:
                return {"status": "ok", "mensagem": "Planilha vazia", "dados": []}

            # Primeira linha é cabeçalho
            headers = values[0] if values else []
            rows = values[1:] if len(values) > 1 else []

            dados = []
            for row in rows:
                item = {}
                for i, header in enumerate(headers):
                    item[header] = row[i] if i < len(row) else ""
                dados.append(item)

            return {
                "status": "ok",
                "total": len(dados),
                "dados": dados
            }

        except Exception as e:
            return {"erro": str(e)}

    def _extract_text_from_pdf(self, file_content: bytes, password: Optional[str] = None) -> Optional[str]:
        """Extrai texto de PDF usando pdfplumber"""
        try:
            pdf_file = io.BytesIO(file_content)
            open_params = {}
            if password:
                open_params['password'] = password

            with pdfplumber.open(pdf_file, **open_params) as pdf:
                text = ""
                for page in pdf.pages:
                    try:
                        page_text = page.extract_text(
                            x_tolerance=1,
                            y_tolerance=1,
                            keep_blank_chars=False,
                            use_text_flow=False
                        )
                        if page_text:
                            text += page_text + "\n"
                    except:
                        continue

                return text.strip().replace('@', '') if text else None
        except:
            return None

    def _extract_trades_from_text(self, text: str) -> Dict:
        """Extrai dados de negociação do texto"""
        trades = []

        trade_pattern = re.compile(
            r'^(?P<num_neg>\d+-[A-Z]+)\s+'
            r'(?P<cv>[CV])\s+'
            r'(?P<mercado>[A-ZÇÃÉÓÚÍ]+)\s+'
            r'(?P<ativo>[A-Z0-9\s]+?)\s+'
            r'(?P<qtd>\d+)\s+'
            r'(?P<preco>[\d\.,]+)\s+'
            r'(?P<valor>[\d\.,]+)\s+'
            r'(?P<dc>[CD])'
        )

        date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
        trade_date = date_match.group() if date_match else None

        for line in text.split('\n'):
            line = line.strip()
            if not line or 'Q Negociação' in line:
                continue

            match = trade_pattern.search(line)
            if match:
                try:
                    asset = re.sub(r'[@#*]\s*$', '', match.group('ativo')).strip()
                    trades.append({
                        'data': trade_date,
                        'num_negociacao': match.group('num_neg'),
                        'operacao': 'Compra' if match.group('cv') == 'C' else 'Venda',
                        'mercado': match.group('mercado'),
                        'ativo': asset,
                        'quantidade': int(match.group('qtd')),
                        'preco': float(match.group('preco').replace('.', '').replace(',', '.')),
                        'valor': float(match.group('valor').replace('.', '').replace(',', '.')),
                        'natureza': match.group('dc')
                    })
                except:
                    continue

        return {'trades': trades}

    def _append_to_sheet(self, sheets_service, sheets_id: str, trade: Dict):
        """Adiciona uma negociação na planilha"""
        row_data = [
            trade.get('data', ''),
            trade.get('ativo', ''),
            trade.get('operacao', ''),
            trade.get('quantidade', ''),
            f"{trade.get('preco', 0.0):.2f}".replace('.', ','),
            f"{trade.get('valor', 0.0):.2f}".replace('.', ','),
        ]

        sheet_name = "Negociações"

        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=sheets_id,
            range=f"{sheet_name}!A:A"
        ).execute()
        next_row = len(result.get('values', [])) + 1

        sheets_service.spreadsheets().values().append(
            spreadsheetId=sheets_id,
            range=f"{sheet_name}!A{next_row}",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [row_data], "majorDimension": "ROWS"}
        ).execute()

    def _mark_as_processed(self, drive_service, file_id: str, original_name: str, status: str):
        """Marca arquivo como processado"""
        try:
            new_name = f"[PROCESSADO_{status}] {original_name}"
            drive_service.files().update(
                fileId=file_id,
                body={'name': new_name},
                fields='name'
            ).execute()
        except:
            pass

    def executar_fluxo_completo_rico(self) -> dict:
        """
        Executa o fluxo completo de processamento de emails da Rico:
        1. Busca emails da Rico com anexos PDF
        2. Extrai PDFs e envia para o Google Drive
        3. Processa PDFs e extrai negociações
        4. Atualiza planilha com as negociações
        5. Marca emails como lidos

        Este é o método principal que deve ser chamado para processar emails da Rico.

        Returns:
            Relatório completo do processamento
        """
        resultado = {
            "status": "ok",
            "etapas": [],
            "resumo": {
                "emails_processados": 0,
                "pdfs_enviados_drive": 0,
                "pdfs_processados": 0,
                "negociacoes_registradas": 0,
                "emails_marcados_lidos": 0,
                "erros": []
            }
        }

        gmail = self._get_gmail()
        drive = self._get_drive()
        sheets = self._get_sheets()

        if not gmail or not drive:
            return {"erro": "Serviços Gmail/Drive não disponíveis. Verifique a conexão."}

        folder_id = os.getenv("FOLDER_ID")
        sheets_id = os.getenv("SHEETS_ID")

        if not folder_id:
            return {"erro": "FOLDER_ID não configurado no .env"}

        try:
            # ===== ETAPA 1: Buscar emails da Rico =====
            resultado["etapas"].append("🔍 Buscando emails da Rico...")

            # Buscar tanto emails lidos quanto não lidos com anexos
            query = "(from:no-reply@rico.com.vc OR from:noreply@rico.com.vc) has:attachment"

            all_messages = []
            page_token = None

            while True:
                results = gmail.users().messages().list(
                    userId='me',
                    q=query,
                    maxResults=100,
                    pageToken=page_token
                ).execute()

                messages = results.get('messages', [])
                if not messages:
                    break

                all_messages.extend(messages)
                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            if not all_messages:
                resultado["etapas"].append("ℹ️ Nenhum email da Rico encontrado")
                return resultado

            resultado["etapas"].append(f"✅ Encontrados {len(all_messages)} emails da Rico")

            # ===== ETAPA 2: Processar cada email =====
            for message in all_messages:
                try:
                    msg = gmail.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()

                    headers = {h['name']: h['value'] for h in msg['payload']['headers']}
                    assunto = headers.get('Subject', 'Sem assunto')

                    # Verificar se tem partes (anexos)
                    if 'parts' not in msg['payload']:
                        continue

                    email_tem_pdf = False

                    for part in msg['payload']['parts']:
                        if not part.get('filename') or not part['filename'].lower().endswith('.pdf'):
                            continue

                        filename = part['filename']

                        # Verificar se já existe no Drive
                        existing = drive.files().list(
                            q=f"'{folder_id}' in parents and name contains '{filename.split('.')[0]}'",
                            fields="files(id, name)"
                        ).execute()

                        if existing.get('files'):
                            # Já existe, pular mas ainda marcar email como lido
                            email_tem_pdf = True
                            continue

                        # ===== ETAPA 2a: Extrair PDF e enviar para Drive =====
                        if 'body' in part and 'attachmentId' in part['body']:
                            attachment_id = part['body']['attachmentId']
                            attachment = gmail.users().messages().attachments().get(
                                userId='me',
                                messageId=message['id'],
                                id=attachment_id
                            ).execute()

                            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                            # Upload para o Drive
                            file_metadata = {
                                'name': filename,
                                'mimeType': 'application/pdf',
                                'parents': [folder_id]
                            }

                            media = MediaIoBaseUpload(
                                io.BytesIO(file_data),
                                mimetype='application/pdf',
                                resumable=True
                            )

                            uploaded_file = drive.files().create(
                                body=file_metadata,
                                media_body=media,
                                fields='id,name,webViewLink'
                            ).execute()

                            resultado["resumo"]["pdfs_enviados_drive"] += 1
                            email_tem_pdf = True

                            # ===== ETAPA 2b: Processar PDF e extrair negociações =====
                            if sheets and sheets_id:
                                text = self._extract_text_from_pdf(
                                    file_data,
                                    password=os.getenv("PDF_PASSWORD")
                                )

                                if text:
                                    data = self._extract_trades_from_text(text)

                                    if data.get('trades'):
                                        for trade in data['trades']:
                                            self._append_to_sheet(sheets, sheets_id, trade)
                                            resultado["resumo"]["negociacoes_registradas"] += 1

                                        resultado["resumo"]["pdfs_processados"] += 1

                                        # Renomear arquivo no Drive como processado
                                        self._mark_as_processed(
                                            drive,
                                            uploaded_file['id'],
                                            filename,
                                            "SUCESSO"
                                        )

                    # ===== ETAPA 3: Marcar email como lido =====
                    if email_tem_pdf:
                        gmail.users().messages().modify(
                            userId='me',
                            id=message['id'],
                            body={'removeLabelIds': ['UNREAD']}
                        ).execute()
                        resultado["resumo"]["emails_marcados_lidos"] += 1

                    resultado["resumo"]["emails_processados"] += 1

                except Exception as e:
                    resultado["resumo"]["erros"].append(f"Erro no email: {str(e)[:50]}")
                    continue

            # ===== RESUMO FINAL =====
            resultado["etapas"].append(f"📧 Emails processados: {resultado['resumo']['emails_processados']}")
            resultado["etapas"].append(f"📄 PDFs enviados ao Drive: {resultado['resumo']['pdfs_enviados_drive']}")
            resultado["etapas"].append(f"📊 PDFs com negociações extraídas: {resultado['resumo']['pdfs_processados']}")
            resultado["etapas"].append(f"📝 Negociações registradas na planilha: {resultado['resumo']['negociacoes_registradas']}")
            resultado["etapas"].append(f"✅ Emails marcados como lidos: {resultado['resumo']['emails_marcados_lidos']}")

            if resultado["resumo"]["erros"]:
                resultado["etapas"].append(f"⚠️ Erros encontrados: {len(resultado['resumo']['erros'])}")

            return resultado

        except Exception as e:
            return {"erro": str(e), "etapas": resultado["etapas"]}
