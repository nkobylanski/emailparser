# emailParser

### Requisites

- Install the following python dependencies (python 3.12.x)

```python
pip install flask requests email beautifulsoup4 lxml google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client google-cloud-pubsub
```

### Instructions

- Run the `quickstart.py` script, a pop-up will appear asking to log-in with your gmail account. Once you select your account, the following will appear:

![Captura de pantalla (2)](https://github.com/user-attachments/assets/ba008e37-4211-43e2-8563-e726f120766b)

![Captura de pantalla (3)](https://github.com/user-attachments/assets/915cda57-e155-48fa-a8f7-95763df05cd1)

- Finally, allow emailParser to access your google account.

![Captura de pantalla (4)](https://github.com/user-attachments/assets/dd42b2fe-0bf0-4cd0-9aad-2f803ef7a8c5)

- Now run the `main.py` script to receive your emails into a JSON format. If the program doesn't automatically create a **"parsed_emails"** folder, go ahead and create it in the same directory. You can also visualize your JSON files in your browser: `http://127.0.0.1:5000`.

### Disclaimers

- Gmail API refreshes after a certain time (usually an hour) so you will need to rerun the `quickstart.py` for it to refresh the `token.json`.
- Gmail API has a request limit with a 24-hour cooldown.
- Attachments are handled and saved locally.
