import threading
import time
from app import app, load_latest_email
from fetch_emails import get_service, fetch_emails

def email_monitor():
    service = get_service()
    if service:
        while True:
            fetch_emails(service)
            load_latest_email()
            time.sleep(10)

if __name__ == '__main__':
    threading.Thread(target=email_monitor, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
