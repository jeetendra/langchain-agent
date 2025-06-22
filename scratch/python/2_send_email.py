import requests
import os
from dotenv import load_dotenv
load_dotenv()

email_server = os.environ.get("EMAIL_SERVER")
email_receiver = os.environ.get("EMAIL_RECEIVER")
api_key = os.environ.get("EMAIL_API_KEY")

if email_server and email_receiver:
    payload = {
        "to": email_receiver,
        "subject": "Task completed",
        "message": "We have completed task 101."
    }

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": api_key
    }

    response = requests.post(email_server, json=payload, headers=headers)

    print("Status:", response.status_code)
    print("Response:", response.json())