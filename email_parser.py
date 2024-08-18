import json
import os
import re
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
    decoded_parts = [part.decode(encoding or 'utf-8') if isinstance(part, bytes) else part 
                     for part, encoding in decode_header(text)]
    return ''.join(decoded_parts)

def parse_email_from_message(msg):
    encoded_sender_name, sender_email = parseaddr(msg['From'])
    sender_name = decode_mime_words(encoded_sender_name)
    
    subject = decode_mime_words(msg['Subject'])
    message_body, links = set(), []

    def process_text(part_text):
        part_text = part_text.replace('\r', '').replace('\n', ' ').strip()
        links.extend(extract_links(part_text))
        return re.sub(r'(https?://\S+)', '', part_text)

    for part in msg.walk() if msg.is_multipart() else [msg]:
        content_type = part.get_content_type()
        if "attachment" not in part.get("Content-Disposition", ""):
            if content_type == "text/plain":
                processed_text = process_text(part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore'))
                message_body.add(processed_text)
            elif content_type == "text/html":
                html_content = part.get_payload(decode=True).decode(part.get_content_charset() or 'utf-8', errors='ignore')
                processed_text = process_text(html_to_text(html_content))
                message_body.add(processed_text)

    email_data = OrderedDict([
        ('From', sender_name.strip()),  # Strip any leading or trailing spaces
        ('Sender_Email', sender_email),
        ('Subject', subject.strip()),
        ('Message', " ".join(message_body).strip()),
        ('Links', links)
    ])

    return email_data

def save_as_json(data, output_dir):
    # Get the subject and replace invalid filename characters with underscores
    subject = data['Subject']
    safe_subject = re.sub(r'[<>:"/\\|?*]', '_', subject)

    # Define the output file path
    file_path = os.path.join(output_dir, f"{safe_subject}.json")

    os.makedirs(output_dir, exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Email data has been saved to {file_path}")

if __name__ == '__main__':
    print("This script is designed to be used as a module. Please import and use the functions directly.")
