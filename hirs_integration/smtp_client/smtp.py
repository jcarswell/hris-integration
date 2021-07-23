import smtplib
import logging

from distutils.util import strtobool
from email.message import EmailMessage

from .helpers import config
from .exceptions import ConfigError,SmtpServerError,SmtpToInvalid

logger = logging.getLogger('SMTP')

class Smtp:
    def __init__(self):
        config_data = config.get_config_cat(config.CAT_CONFIG)

        prefix = config.get_config(config.CAT_EMAIL,config.EMAIL_PREFIX) or None
        if prefix and prefix[-1] != ' ':
            prefix += ' '
        elif not prefix:
            prefix = ''
        self.prefix = prefix

        if strtobool(config_data[config.SERVER_SSL]):
            self.smtp_class = smtplib.SMTP_SSL
        else:
            self.smtp_class = smtplib.SMTP

        self.server = config_data[config.SERVER_SERVER]
        self.port = config_data[config.SERVER_PORT] or 0
        self.tls = strtobool(config_data[config.SERVER_TLS])
        self.username = config_data[config.SERVER_USERNAME] or None
        if self.username:
            self.password = config_data[config.SERVER_PASSWORD]
        else:
            self.password = None
        self.sender = config_data[config.SERVER_SENDER]

    def connect(self):
        try:
            self.__conn = self.smtp_class(host=self.server,port=self.port)
            self.__conn.ehlo()
            if self.tls and isinstance(self.__conn,smtplib.SMTP):
                self.__conn.starttls
                self.__conn.ehlo()
            
            if self.username and self.password:
                self.__conn.login(user=self.username,password=self.password)
        except smtplib.SMTPHeloError:
            logger.critical("SMTP Server is invalid")
            return False
        except smtplib.SMTPAuthenticationError:
            logger.critical("Invalid Authentication")
            raise ConfigError("Provide username password combination were rejected by the server")
        except smtplib.SMTPNotSupportedError as e:
            logger.exception("Server threw a not support error")
            raise SmtpServerError from e

    def close(self):
        self.__conn.quit()
        del self.__conn

    def send(self,to,msg:str,subject:str):
        email = EmailMessage()
        email.set_content(msg)
        email['Subject'] = self.prefix + subject
        email['To'] = to
        email['From'] = self.sender
        
        self.connect()
        try:
            self.__conn.send_message(email,self.sender,to)
        except smtplib.SMTPSenderRefused as e:
            logger.exception('sender does not have premission to send emails')
            raise ConfigError("Sender does not have permission on the server") from e
        except smtplib.SMTPRecipientsRefused:
            logger.exception("to address(es) were rejected by the server")
            raise SmtpToInvalid(f"to {to} was rejected be the server")
        
        self.close()