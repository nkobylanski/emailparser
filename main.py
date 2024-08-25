import threading
from app import app
from fetch_emails import get_service, fetch_emails

def email_monitor():
    service = get_service()
    if service:
        while True:
            fetch_emails(service)

if __name__ == '__main__':
    threading.Thread(target=email_monitor, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
