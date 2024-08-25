import os
import re
import json
from bs4 import BeautifulSoup
from email.header import decode_header
from email.utils import parseaddr
from collections import OrderedDict

def html_to_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(["script", "style"]):
        tag.decompose()
    return ' '.join(soup.get_text(separator="\n").split())

def extract_links(text):
    return re.findall(r'(https?://\S+)', text)

def decode_mime_words(text):
    return ''.join(part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part 
                   for part, encoding in decode_header(text))

def save_attachment(part, save_dir):
    filename = decode_mime_words(part.get_filename())
    if filename:
        filepath = os.path.join(save_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(part.get_payload(decode=True))
        print(f"Attachment saved to {filepath}")

def parse_email_from_message(msg):
    sender_name, sender_email = parseaddr(msg['From'])
    subject = decode_mime_words(msg['Subject']).strip()
    safe_subject = re.sub(r'[<>:"/\\|?*]', '_', subject)
    message_body, links = set(), []

    def process_text(text):
        text = text.replace('\r', '').replace('\n', ' ').strip()
        links.extend(extract_links(text))
        return re.sub(r'(https?://\S+)', '', text)

    attachments, save_dir = False, None
    for part in msg.walk() if msg.is_multipart() else [msg]:
        if "attachment" in part.get("Content-Disposition", ""):
            if not attachments:
                save_dir = os.path.join('parsed_emails', safe_subject)
                os.makedirs(save_dir, exist_ok=True)
            attachments = True
            save_attachment(part, save_dir)
        elif part.get_content_type() == "text/plain":
            message_body.add(process_text(part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8')))
        elif part.get_content_type() == "text/html":
            message_body.add(process_text(html_to_text(part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8'))))

    email_data = OrderedDict([('From', sender_name), ('Sender_Email', sender_email), 
                              ('Subject', subject), ('Message', " ".join(message_body)), ('Links', links)])
    return email_data, attachments, save_dir

def save_as_json(data, output_dir, save_dir, attachments):
    file_path = os.path.join(save_dir or output_dir, f"{re.sub(r'[<>:"/\\|?*]', '_', data['Subject'])}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Email saved to {file_path}")
    return file_path
