from apiflask import APIFlask, Schema, fields
from datetime import datetime, timezone
from email.message import EmailMessage
import smtplib
import env


class Sender:
    def __init__(self):
        self.client = self.get_smtp_client()

    @staticmethod
    def get_smtp_client():
        client = smtplib.SMTP_SSL(env.smtp_host, env.smtp_port)
        client.ehlo()
        client.login(env.smtp_username, env.smtp_password)
        return client

    @staticmethod
    def build_message(
        to, message, title, name_from=None, name_to=None, subtype="plain"
    ):
        msg = EmailMessage()
        msg["Subject"] = title
        msg["From"] = (
            f"{name_from} <{env.smtp_username}>" if name_from else env.smtp_username
        )
        msg["To"] = f"{name_to} <{to}>" if name_to else to
        msg["Date"] = (
            datetime.utcnow()
            .replace(tzinfo=timezone.utc)
            .strftime("%a, %d %b %Y %H:%M:%S %z")
        )
        msg.set_content(message, charset="utf-8", subtype=subtype)
        return msg

    def send_to(
        self,
        to: str,
        message: str,
        title: str,
        name_from: str = None,
        name_to: str = None,
    ):
        message = self.build_message(to, message, title, name_from, name_to)
        try:
            self.client.send_message(message)
        except smtplib.SMTPServerDisconnected:
            self.client = self.get_smtp_client()
            self.client.send_message(message)

        return message.as_string()


sender = Sender()

app = APIFlask(__name__, docs_ui="elements")


class PostIn(Schema):
    to: str = fields.Email(required=True)
    message: str = fields.String(required=True)
    title: str = fields.String(required=True)
    name_from: str = fields.String(data_key="nameFrom", default=None)
    name_to: str = fields.String(data_key="nameTo", default=None)
    sybtype: str = fields.String(data_key="subType", default="plain")


@app.post("/sendmail")
@app.input(PostIn)
def send_mail(data: dict):
    return sender.send_to(**data)


@app.get("/")
def root():
    return ""
