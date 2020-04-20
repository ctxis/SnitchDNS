from flask import current_app
from flask_mail import Mail, Message


class EmailManager:
    def __init__(self, hostname, port, username, password, sender, tls):
        current_app.config['MAIL_SERVER'] = hostname
        current_app.config['MAIL_PORT'] = port
        current_app.config['MAIL_USERNAME'] = username
        current_app.config['MAIL_PASSWORD'] = password
        current_app.config['MAIL_DEFAULT_SENDER'] = sender
        current_app.config['MAIL_USE_TLS'] = tls

        self.__hostname = hostname
        self.__port = port
        self.__tls = tls
        self.__username = username
        self.__password = password

        self.__mail = Mail(current_app)

    def send(self, recipients, subject, body):
        if isinstance(recipients, str):
            recipients = [recipients]

        message = Message()
        message.subject = subject
        message.body = body
        message.recipients = recipients

        return self.send_message(message)

    def send_message(self, message):
        try:
            self.__mail.send(message)
        except Exception as e:
            return e

        return True
