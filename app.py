from flask import Flask, jsonify, render_template, Response
import os
import json
import threading
import time
from fetch_emails import get_service, fetch_emails
from collections import OrderedDict

app = Flask(__name__)

latest_email_data = None  # Global variable to store the latest parsed email data
PARSED_EMAILS_FOLDER = 'parsed_emails'

def load_latest_email():
    global latest_email_data
    json_files = [f for f in os.listdir(PARSED_EMAILS_FOLDER) if f.endswith('.json')]
    if json_files:
        latest_file = max(json_files, key=lambda x: os.path.getctime(os.path.join(PARSED_EMAILS_FOLDER, x)))
        with open(os.path.join(PARSED_EMAILS_FOLDER, latest_file), 'r', encoding='utf-8') as f:
            latest_email_data = json.load(f, object_pairs_hook=OrderedDict)
            debug_print("Loaded email data:", latest_email_data)

def email_monitor():
    service = get_service()
    if service:
        while True:
            debug_print("Checking for new emails...")
            fetch_emails(service)
            load_latest_email()
            time.sleep(10)  # Check for new emails every 10 seconds

def debug_print(*args):
    print(*args)

@app.route('/')
def index():
    debug_print("Rendering index with data:", latest_email_data)
    return render_template('index.html', email_data=latest_email_data), 200, {'Content-Type': 'text/html; charset=utf-8'}

@app.route('/api/email')
def api_email():
    if latest_email_data:
        json_str = json.dumps(latest_email_data, ensure_ascii=False, indent=4)
        debug_print("Returning JSON data:", json_str)
        return Response(json_str, content_type='application/json; charset=utf-8')
    else:
        return jsonify({"error": "No emails parsed yet"})

if __name__ == '__main__':
    threading.Thread(target=email_monitor, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
