import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

# Configuration - replace with your SMTP server details or load from environment/config
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'soravang81@gmail.com'  # Replace with your email
SMTP_PASSWORD = 'nxtz lxuu inqn uaft'         # Replace with your app password or real password
SENDER_EMAIL = SMTP_USERNAME


def send_email(to_email: str, subject: str, body: str, html: Optional[str] = None):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email

    part1 = MIMEText(body, 'plain')
    msg.attach(part1)
    if html:
        part2 = MIMEText(html, 'html')
        msg.attach(part2)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")
