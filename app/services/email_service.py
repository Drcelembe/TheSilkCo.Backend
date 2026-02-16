from flask import current_app
from flask_mail import Message
from database import db
from flask_mail import Mail

mail = Mail()

def init_mail(app):
    mail.init_app(app)

def send_simple_email(subject, recipients, body):
    app = current_app._get_current_object()
    msg = Message(subject=subject, recipients=recipients)
    msg.body = body
    try:
        mail.send(msg)
        return True
    except Exception as e:
        app.logger.error("email send failed: %s", e)
        return False
