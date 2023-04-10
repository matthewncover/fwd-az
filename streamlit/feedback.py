import os
from dotenv import load_dotenv
import smtplib, ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

def send_email(subject, text, recipient="matthew"):

    port = 465
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv(f"RECEIVER_EMAIL_{str.upper(recipient)}")
    password = os.getenv("APP_PASSWORD")


    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    part1 = MIMEText(text, "html")
    message.attach(part1)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)

        server.sendmail(sender_email, receiver_email, message.as_string())