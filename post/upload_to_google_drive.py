#pip install google-api-python-client
import os
from googleapiclient.discovery import build
from google.oauth2 import service_account
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service_account.json'
API_NAME = 'drive'
API_VERSION = 'v3'
PARENT_FOLDER_ID = '1aYy26AQCwlDb0Amj8Si8AEnIhW6DPsc4' #the last part in google drive folder url 

def authenticate():
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return credentials

def upload_image_to_google_drive(file_paths):
    creds = authenticate()
    service = build(API_NAME, API_VERSION, credentials=creds)

    uploaded_file_urls = []

    # rename the image name
    for file_path in file_paths:
        file_name = os.path.basename(file_path)

        file_metadata = {
            'name': file_name,
            'parents':[PARENT_FOLDER_ID],
        }

        # Upload the file
        response = service.files().create(
            body = file_metadata,
            media_body = file_path,
            fields='id,webViewLink'
        ).execute()

        file_url = response.get('webViewLink')
        uploaded_file_urls.append(file_url)
    
    return uploaded_file_urls

    
