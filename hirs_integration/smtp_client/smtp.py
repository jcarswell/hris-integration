import smtplib
import logging

from distutils.util import strtobool
from email.message import EmailMessage
from typing import List, Union, AnyStr

from .helpers import config
from .exceptions import ConfigError,SmtpServerError,SmtpToInvalid

logger = logging.getLogger('SMTP')

class Smtp:
    """SMTP Client is a wrapper for the built-in SMTP library. Used for sending emails to 
        a set of target recipient(s).
        
        Usage:
        s = Smtp()
        s.send([recipient(s)],[email body],[subject]) 
    """

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
        """Connect to the SMTP Server and send an EHLO"""
        logger.debug(f"connecting to SMTP Server {self.server} on port {self.port}")
        try:
            self.__conn = self.smtp_class(host=self.server,port=self.port)
            self.__conn.ehlo()
            logger.debug(f"Connect and sent EHLO to server")
            if self.tls and isinstance(self.__conn,smtplib.SMTP):
                self.__conn.starttls()
                self.__conn.ehlo()
                logger.debug("Started a TLS session")

            if self.username and self.password:
                self.__conn.login(user=self.username,password=self.password)
                logger.debug(f"Logged into the server")
        except smtplib.SMTPHeloError as e:
            logger.critical("SMTP Server is invalid")
            raise SmtpServerError("Server not valid") from e
        except smtplib.SMTPAuthenticationError:
            logger.critical("Invalid Authentication")
            raise ConfigError("Provide username password combination were rejected by the server")
        except smtplib.SMTPNotSupportedError as e:
            logger.exception("Server threw a not support error")
            raise SmtpServerError from e

    def close(self):
        self.__conn.quit()
        del self.__conn
        logger.debug("Server connection closed. Until next time.")

    def send(self,to:Union[AnyStr,List],msg:str,subject:str):
        """Send an email message to the target recepient(s)

        Args:
            to (Str,List): A list of target email addresses
            msg (str): The body of the email
            subject (str): Subject line

        Raises:
            ValueError: Invalid to type
            ConfigError: Authentication with the server failed
            SmtpToInvalid: one or more requested target email address(es) rejected by the server
            SmtpServerError: SMTP Configuration is invalid
        """
        if isinstance(to,str):
            to = to.split(',')
        elif not isinstance(to,list):
            raise ValueError(f"'to' should be a string or list, got {type(to)}")
        email = EmailMessage()
        email.set_content(msg)
        email['Subject'] = self.prefix + subject
        email['To'] = to
        email['From'] = self.sender
        
        self.connect()
        try:
            logger.debug(f"Trying to send email to {to}")
            self.__conn.send_message(email,self.sender,to)
        except smtplib.SMTPSenderRefused as e:
            logger.exception('sender does not have premission to send emails')
            raise ConfigError("Sender does not have permission on the server") from e
        except smtplib.SMTPRecipientsRefused as e:
            errors = []
            for u in to:
                errors.append(f"Code: {e.recipients[u][0]}, Message: {e.recipients[u][1]}")
            e_str = '\n\t'.join(errors)
            logger.exception(f"Send email failed with the following errors \n\t{e_str}")
            raise SmtpToInvalid(f"Recievied the following errors \n\t{e_str}")
        
        self.close()