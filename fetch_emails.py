import os
import json
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email import message_from_bytes
from email_parser import parse_email_from_message, save_as_json

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_service():
    try:
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            raise ValueError("Invalid credentials, run 'python quickstart.py' to authorize the application.")
        return build('gmail', 'v1', credentials=creds)
    except HttpError as error:
        handle_error(f'An error occurred: {error}')

def fetch_emails(service, user_id='me'):
    try:
        response = service.users().messages().list(userId=user_id, q='is:unread').execute()
        messages = response.get('messages', [])
        if not messages:
            print('No new messages.')
            return
        for msg in messages:
            msg_id = msg['id']
            message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
            msg_obj = message_from_bytes(base64.urlsafe_b64decode(message['raw'].encode('UTF-8')))
            
            email_data = parse_email_from_message(msg_obj)
            save_as_json(email_data, 'parsed_emails')
            
            service.users().messages().modify(userId=user_id, id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
    except HttpError as error:
        handle_error(f'An error occurred: {error}')

def handle_error(message):
    print(message)

if __name__ == '__main__':
    service = get_service()
    if service:
        fetch_emails(service)
