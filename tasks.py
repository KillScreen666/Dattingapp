import os
import requests
from dotenv import load_dotenv

load_dotenv()

DOMAIN = os.getenv("MAILGUN_DOMAIN")

def send_email(to, subject, body, html):
    return requests.post(
        f"https://api.mailgun.net/v3/{DOMAIN}/messages",
        auth=("api", os.getenv("MAILGUN_API_KEY")),
        data={"from": f"Your Name <mailgun@{DOMAIN}>",
            "to": [to],
            "subject": subject,
            "text": body,
            "html": html
        }
    )

def send_user_registration_email(email, username):
    return send_email(
        email,
        "Successfully signed up",
        f"Hi {username}! You have successfully signed up to the Stores REST API.",
    )