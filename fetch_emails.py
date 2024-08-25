import os
import base64
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email import message_from_bytes
from email_parser import parse_email_from_message, save_as_json
from collections import OrderedDict

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
PARSED_EMAILS_FOLDER = 'parsed_emails'

def get_service():
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if creds and creds.valid:
            return build('gmail', 'v1', credentials=creds)
    print("Run 'python quickstart.py' to authorize the app.")
    return None

def fetch_emails(service):
    try:
        messages = service.users().messages().list(userId='me', q='is:unread').execute().get('messages', [])
        for msg in messages:
            msg_obj = message_from_bytes(base64.urlsafe_b64decode(service.users().messages().get(userId='me', id=msg['id'], format='raw').execute()['raw'].encode('UTF-8')))
            email_data, attachments, save_dir = parse_email_from_message(msg_obj)
            save_as_json(email_data, PARSED_EMAILS_FOLDER, save_dir, attachments)
            service.users().messages().modify(userId='me', id=msg['id'], body={'removeLabelIds': ['UNREAD']}).execute()
    except HttpError as error:
        print(f'Error: {error}')

def load_all_emails():
    email_files = []
    for root, _, files in os.walk(PARSED_EMAILS_FOLDER):
        for file in files:
            if file.endswith('.json'):
                email_files.append(os.path.join(root, file))

    email_files.sort(key=os.path.getctime, reverse=True)

    all_emails = []
    for email_file in email_files:
        with open(email_file, 'r', encoding='utf-8') as f:
            all_emails.append(json.load(f, object_pairs_hook=OrderedDict))
    return all_emails