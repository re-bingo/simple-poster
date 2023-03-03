from apiflask import APIFlask, Schema, fields
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import env


class Sender:
    def __init__(self):
        self.client = smtplib.SMTP_SSL(env.smtp_host, env.smtp_port)
        self.client.ehlo()
        self.client.login(env.smtp_username, env.smtp_password)

    def send_to(self, to: str, message: str, title: str, name_from: str, name_to: str):
        body = MIMEText(message)
        body["From"] = Header(f"{name_from}<{env.smtp_username}>", "utf-8")
        body["To"] = Header(f"{name_to}<{to}>", "utf-8")
        body["Subject"] = Header(title, "utf-8")
        self.client.sendmail(env.smtp_username, to, body.as_bytes())
        return body.as_string()


sender = Sender()

app = APIFlask(__name__, docs_ui="elements")


class PostIn(Schema):
    to: str = fields.Email(required=True)
    message: str = fields.String(required=True)
    title: str = fields.String(required=True)
    name_from: str = fields.String(required=True, data_key="nameFrom")
    name_to: str = fields.String(required=True, data_key="nameTo")


@app.post("/sendmail")
@app.input(PostIn)
def send_mail(data: dict):
    return sender.send_to(**data)


@app.get("/")
def root():
    return ""
