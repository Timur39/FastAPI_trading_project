import smtplib
from email.message import EmailMessage

from celery import Celery
from config import SMTP_PASSWORD, SMTP_USER, REDIS_HOST, REDIS_PORT

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465

celery = Celery('tasks', broker=f'redis://{REDIS_HOST}:{REDIS_PORT}')


def get_email_template_dashboard(username: str):
    email = EmailMessage()
    email['Subject'] = 'Трейдинг и точка Отчет Дашборд'
    email['From'] = SMTP_USER
    email['To'] = SMTP_USER

    email.set_content(
        f'''
        <h1>Добро пожаловать в трейдинг и точку</h1>
        <p>Ваш логин: {username}</p>
        <p>Ваш отчет: ?</p> 
        ''',
        subtype='html'
    )
    return email


@celery.task
def send_email_report_dashboard(username: str):
    email = get_email_template_dashboard(username)
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(email)