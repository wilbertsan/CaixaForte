from __future__ import print_function
import os
import io
import base64
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv

# Esse Script monitora o email do cliente e verifica se existe emails recebidos
# de no-reply@rico.com.vc e envia o arquivo pdf em anexo para um pasta no GoogleDrive

load_dotenv()
# Se modificar esses escopos, delete o arquivo token.json
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/gmail.modify'
]

def get_gmail_service():
    """Autentica e retorna o serviço Gmail"""
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
    
    return build('gmail', 'v1', credentials=creds)

def get_drive_service():
    """Autentica e retorna o serviço Drive"""
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
    
    return build('drive', 'v3', credentials=creds)

##################################################################################

def upload_to_drive(drive_service, file_data, filename, folder_id=None):
    """Envia arquivo para o Google Drive"""
    file_metadata = {
        'name': filename,
        'mimeType': 'application/pdf'
    }
    if folder_id:
        file_metadata['parents'] = [folder_id]
    
    media = MediaIoBaseUpload(io.BytesIO(file_data),
                            mimetype='application/pdf',
                            resumable=True)
    
    file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,name,webViewLink'
    ).execute()
    
    print(f"✅ PDF enviado para o Drive: {file.get('name')}")
    print(f"🔗 Link: {file.get('webViewLink')}")
    return file

##################################################################################

def process_pdf_attachments(service, drive_service, folder_id=None):
    """Processa anexos PDF dos e-mails"""
    # Busca de ambos os remetentes possíveis da Rico (no-reply e noreply)
    query = "is:unread (from:no-reply@rico.com.vc OR from:noreply@rico.com.vc) has:attachment"
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=10
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("Nenhum e-mail com anexo PDF encontrado.")
        return
    
    print(f"📨 Processando {len(messages)} e-mails com anexos PDF...")
    
    for message in messages:
        msg = service.users().messages().get(
            userId='me',
            id=message['id'],
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        print(f"\n📧 Assunto: {headers.get('Subject', '')}")
        
        # Processar partes do e-mail
        for part in msg['payload']['parts']:
            if part.get('filename') and part['filename'].lower().endswith('.pdf'):
                filename = part['filename']
                print(f"📄 Anexo encontrado: {filename}")
                
                if 'body' in part and 'attachmentId' in part['body']:
                    attachment_id = part['body']['attachmentId']
                    attachment = service.users().messages().attachments().get(
                        userId='me',
                        messageId=message['id'],
                        id=attachment_id
                    ).execute()
                    
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                    upload_to_drive(drive_service, file_data, filename, folder_id)
                    
                    # Marcar como lido (opcional)
                    service.users().messages().modify(
                        userId='me',
                        id=message['id'],
                        body={'removeLabelIds': ['UNREAD']}
                    ).execute()

##################################################################################

def main():
    # Obter serviços
    gmail_service = get_gmail_service()
    drive_service = get_drive_service()
    
    if gmail_service and drive_service:
        # ID da pasta de destino no Drive (opcional)
        # folder_id = '1XyZ...'  # Substitua pelo ID da sua pasta
        folder_id = os.getenv("FOLDER_ID")
        
        process_pdf_attachments(gmail_service, drive_service, folder_id)

if __name__ == '__main__':
    main()