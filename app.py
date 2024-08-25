from flask import Flask, jsonify, render_template
from fetch_emails import load_all_emails

app = Flask(__name__)

@app.route('/')
def index():
    email_data = load_all_emails()
    return render_template('index.html', email_data=email_data)

@app.route('/api/email')
def api_email():
    return jsonify(load_all_emails())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
