from celery import shared_task
import smtplib
from email.mime.text import MIMEText
from os import getenv


@shared_task
def send_email(body: str, subject: str, to: list[str]):
    sender = getenv("EMAIL_NAME")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(to)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, getenv("EMAIL_PASSWORD"))
    smtp_server.sendmail(sender, to, msg.as_string())
    smtp_server.quit()
