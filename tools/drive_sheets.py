import os
import io
import pdfplumber
import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import Dict, List
from typing import Optional
import re

# Carrega configurações
load_dotenv()

# Escopos necessários
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',    # Para ler emails
    'https://www.googleapis.com/auth/drive.file',        # Para arquivos criados pelo app
    'https://www.googleapis.com/auth/drive.metadata',    # Para renomear arquivos
    'https://www.googleapis.com/auth/spreadsheets',       # Para editar planilhas
    'https://www.googleapis.com/auth/drive'
]

def get_services():
    """Autentica e retorna os serviços Drive e Sheets"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES,
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    drive = build('drive', 'v3', credentials=creds)
    sheets = build('sheets', 'v4', credentials=creds)
    return drive, sheets

def extract_text_from_pdf(file_content: bytes, password: Optional[str] = None) -> Optional[str]:
    """
    Extrai texto de PDF usando pdfplumber, com suporte a senha
    
    Args:
        file_content: Conteúdo binário do PDF
        password: Senha opcional para PDFs criptografados
    
    Returns:
        Texto extraído ou None em caso de falha
    """
    try:
        # Cria um objeto de arquivo em memória
        pdf_file = io.BytesIO(file_content)
        
        # Configurações para PDFs protegidos
        open_params = {}
        if password:
            open_params['password'] = password
        
        with pdfplumber.open(pdf_file, **open_params) as pdf:
            text = ""
            for page in pdf.pages:
                try:
                    # Extrai texto mantendo layout básico
                    page_text = page.extract_text(
                        x_tolerance=1,
                        y_tolerance=1,
                        keep_blank_chars=False,
                        use_text_flow=False
                    )
                    if page_text:
                        text += page_text + "\n"
                
                except Exception as page_error:
                    print(f"⚠️ Erro na página {page.page_number}: {str(page_error)}")
                    continue
            
            return text.strip().replace('@','') if text else None
    
    except pdfplumber.PasswordError:
        print("🔒 PDF criptografado - Senha incorreta ou não fornecida")
        return None
    
    except Exception as e:
        print(f"❌ Erro ao processar PDF: {str(e)}")
        return None
    
def extract_data_from_text(text: str) -> Dict:
    """
    Extrai dados de negociação específicos para o formato da Rico Corretora
    
    Args:
        text: Texto extraído do PDF
        
    Returns:
        {
            'data': str,
            'trades': List[Dict],
            'total_operacoes': int,
            'valor_total': float,
            'saldo': str
        }
    """
    trades = []
    
    # Padrão otimizado para a Rico
    trade_pattern = re.compile(
        r'^(?P<num_neg>\d+-[A-Z]+)\s+'  # Número da negociação (1-BOVESPA)
        r'(?P<cv>[CV])\s+'              # C/V (Compra/Venda)
        r'(?P<mercado>[A-ZÇÃÉÓÚÍ]+)\s+' # Tipo de mercado (FRACIONARIO/VISTA/OPÇÃO)
        r'(?P<ativo>[A-Z0-9\s]+?)\s+'   # Ativo (BRASIL ON NM)
        r'(?P<qtd>\d+)\s+'              # Quantidade
        r'(?P<preco>[\d\.,]+)\s+'       # Preço (20,70)
        r'(?P<valor>[\d\.,]+)\s+'       # Valor total (82,80)
        r'(?P<dc>[CD])'                 # D/C (Débito/Crédito)
    )
    
    # Extrai data do pregão
    date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)
    trade_date = date_match.group() if date_match else None
    
    # Processamento linha a linha
    for line in text.split('\n'):
        line = line.strip()
        if not line or 'Q Negociação' in line:  # Pula cabeçalhos
            continue
            
        match = trade_pattern.search(line)
        if match:
            try:
                trades.append({
                    'data': trade_date,
                    'num_negociacao': match.group('num_neg'),
                    'operacao': 'Compra' if match.group('cv') == 'C' else 'Venda',
                    'mercado': match.group('mercado'),
                    'ativo': clean_asset_name(match.group('ativo')),
                    'quantidade': int(match.group('qtd')),
                    'preco': float(match.group('preco').replace('.', '').replace(',', '.')),
                    'valor': float(match.group('valor').replace('.', '').replace(',', '.')),
                    'natureza': match.group('dc')
                })
            except (ValueError, AttributeError) as e:
                print(f"⚠️ Erro ao processar linha: {line}\nErro: {e}")
                continue
    
    # Cálculo do resumo
    total = sum(trade['valor'] for trade in trades)
    
    return {
        'trades': trades
    }

# Funções auxiliares
def clean_asset_name(asset: str) -> str:
    """Remove caracteres especiais e normaliza nome do ativo"""
    return re.sub(r'[@#*]\s*$', '', asset).strip()


##################################################################################

def update_sheet(sheets_service, data, file_name=None):
    """Atualiza a aba 'Negociações' aceitando lista ou dicionário"""
    try:
        # Converte lista para o formato dicionário se necessário
        if isinstance(data, list):
            data = {
                '_id': file_name.split('-')[1] if file_name else '',
                'trades': [{
                    'data': data[0],
                    'num_negociacao': data[1],
                    'operacao': data[2],
                    'mercado': data[3],
                    'ativo': data[4],
                    'quantidade': data[5],
                    'preco': data[6],
                    'valor': data[7],
                    'natureza': data[8]
                }]
            }
        
        # Extração segura dos dados
        trade_data = data['trades'][0] if isinstance(data.get('trades'), list) else {}
        
        # Prepara a linha para o Google Sheets
        row_data = [
            
            trade_data.get('data', ''),                               # Coluna A: Data
            trade_data.get('ativo', ''),                              # Coluna B: Ativo
            trade_data.get('operacao', ''),                           # Coluna C: Operação
            trade_data.get('quantidade', ''),                         # Coluna D: Quantidade
            f"{trade_data.get('preco', 0.0):.2f}".replace('.', ','),  # Coluna E: Preço Unitário
            f"{trade_data.get('valor', 0.0):.2f}".replace('.', ','),  # Coluna F: Valor Total
        ]
        
        # Configuração do request
        sheet_name = "Negociações"
        body = {
            "values": [row_data],  # Lista de linhas
            "majorDimension": "ROWS"
        }
        
        # Encontra a próxima linha vazia
        range_name = f"{sheet_name}!A:A"
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=os.getenv('SHEETS_ID'),
            range=range_name
        ).execute()
        next_row = len(result.get('values', [])) + 1
        
        # Envia os dados
        sheets_service.spreadsheets().values().append(
            spreadsheetId=os.getenv('SHEETS_ID'),
            range=f"{sheet_name}!A{next_row}",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body=body
        ).execute()
        
        print(f"✅ Dados inseridos na linha {next_row}:")
        
        
    except Exception as e:
        print(f"❌ Erro ao atualizar planilha: {str(e)}")
        raise

def mark_as_processed(drive_service, file_id, original_name, status):
    """Marca o arquivo como processado com status detalhado"""
    try:
        new_name = f"[PROCESSADO_{status}] {original_name}"
        drive_service.files().update(
            fileId=file_id,
            body={'name': new_name},
            fields='name'
        ).execute()
        print(f"📌 Marcado como {status}: {new_name}")
    except Exception as e:
        print(f"⚠️ Falha ao renomear arquivo: {str(e)}")

def process_drive_files(drive_service, sheets_service):
    """Processa arquivos PDF não lidos e envia trades para a planilha"""
    query = f"""
    '{os.getenv('FOLDER_ID')}' in parents and 
    mimeType='application/pdf' and 
    not name contains 'lido' and
    not name contains 'processado'
    """
    
    results = drive_service.files().list(
        q=query,
        pageSize=20,
        fields="files(id, name, createdTime, modifiedTime)",
        orderBy="modifiedTime asc"  # Processa os mais antigos primeiro
    ).execute()
    
    files = results.get('files', [])
    if not files:
        print("✅ Nenhum arquivo novo para processar.")
        return
    
    print(f"\n🔍 Encontrados {len(files)} arquivos para processar...")
    
    for file in files:
        print(f"\n📄 Iniciando processamento: {file['name']}")
        try:
            # 1. Download do arquivo
            request = drive_service.files().get_media(fileId=file['id'])
            file_content = request.execute()
            
            # 2. Extração de texto com tratamento de erro
            text = extract_text_from_pdf(
                file_content,
                password=os.getenv("PDF_PASSWORD")
            )
            if not text:
                print("⏭ Arquivo não legível ou vazio - pulando")
                continue
            
            # 3. Processamento dos dados
            extracted_data = extract_data_from_text(text)
            print(extracted_data)
            #
            if not extracted_data or not extracted_data.get('trades'):
                print("ℹ️ Nenhuma negociação encontrada no arquivo")
                mark_as_processed(drive_service, file['id'], file['name'], "SEM_NEGOCIACOES")
                continue
            
            # 4. Preparação dos dados para a planilha
            sheet_data = prepare_sheet_data(extracted_data)
            print(sheet_data)
            # 5. Envio para o Google Sheets
            update_sheet(
                sheets_service,
                sheet_data,
                file_name=file['name']
            )
            
            # 6. Marca como processado
            mark_as_processed(
                drive_service,
                file['id'],
                file['name'],
                "SUCESSO"
            )
            
            print(f"✅ Processado com sucesso: {len(extracted_data['trades'])} negociações")
            
        except Exception as e:
            print(f"❌ Erro crítico ao processar {file['name']}: {str(e)}")
            mark_as_processed(
                drive_service,
                file['id'],
                file['name'],
                "ERRO"
            )
            continue



def prepare_sheet_data(extracted_data):
    """Prepara os dados no formato para a planilha"""
    sheet_data = []
    
    # Dados das negociações
    for trade in extracted_data['trades']:
        sheet_data.append([
            trade['data'],
            trade['num_negociacao'],
            trade['operacao'],
            trade['mercado'],
            trade['ativo'],
            trade['quantidade'],
            trade['preco'],
            trade['valor'],
            trade['natureza']
        ])
    
    return sheet_data[0]

def main():
    drive, sheets = get_services()
    if drive and sheets:
        process_drive_files(drive, sheets)

if __name__ == '__main__':
    main()