# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import smtplib
import logging

from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Union, AnyStr

from .helpers import config
from .exceptions import ConfigError, SmtpServerError, SmtpToInvalid

logger = logging.getLogger("SMTP")


class Smtp:
    """
    SMTP Client is a wrapper for the built-in SMTP library. Used for sending emails to
    a set of target recipient(s).

    Usage:
    s = Smtp()
    message = s.mime_build(text=[text], html=[html], subject=[subject], to=[to])
    s.send_html([recipient(s)],message)

    """

    def __init__(self):
        self.config = config.Config()
        config_data = self.config.get_category(config.CAT_CONFIG)

        prefix = self.config(config.CAT_EMAIL, config.EMAIL_PREFIX) or None
        if prefix and prefix[-1] != " ":
            prefix += " "
        elif not prefix:
            prefix = ""
        self.prefix = prefix

        if config_data[config.SERVER_SSL]:
            self.smtp_class = smtplib.SMTP_SSL
        else:
            self.smtp_class = smtplib.SMTP

        self.server = config_data[config.SERVER_SERVER]
        self.port = config_data[config.SERVER_PORT] or 0
        self.tls = config_data[config.SERVER_TLS]
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
            self.__conn = self.smtp_class(host=self.server, port=self.port)
            self.__conn.ehlo()
            logger.debug(f"Connect and sent EHLO to server")
            if self.tls and isinstance(self.__conn, smtplib.SMTP):
                self.__conn.starttls()
                self.__conn.ehlo()
                logger.debug("Started a TLS session")

            if self.username and self.password:
                self.__conn.login(user=self.username, password=self.password)
                logger.debug(f"Logged into the server")
        except smtplib.SMTPHeloError as e:
            logger.critical("SMTP Server is invalid")
            raise SmtpServerError("Server not valid") from e
        except smtplib.SMTPAuthenticationError:
            logger.critical("Invalid Authentication")
            raise ConfigError(
                "Provide username password combination were rejected by the server"
            )
        except smtplib.SMTPNotSupportedError as e:
            logger.exception("Server threw a not support error")
            raise SmtpServerError from e

    def close(self):
        """Close and cleanup the SMTP connection"""
        self.__conn.quit()
        del self.__conn
        logger.debug("Server connection closed. Until next time.")

    def mime_build(
        self,
        text: AnyStr = None,
        html: AnyStr = None,
        subject: AnyStr = None,
        to: Union[AnyStr, List[AnyStr]] = None,
    ) -> MIMEMultipart:
        """
        Compose an HTML email message. Either the text or html must be provided, along
        with the subject. The to field can be populated as part of sending the actual
        message.

        :param text: The text version of the message, defaults to None
        :type text: AnyStr, optional
        :param html: The HTML marked up version of the message, defaults to None
        :type html: AnyStr, optional
        :param subject: The subject of the message
        :type subject: AnyStr
        :param to: A list of target email addresses, defaults to None
        :type to: Union[AnyStr, List[AnyStr]], optional
        :raises ValueError: If neither text or html is provided
        :return: The composed MIME message that can be passed to send_html
        :rtype: MIMEMultipart
        """

        if text is None and html is None:
            raise ValueError("both html and text may not be None")

        msg = MIMEMultipart("alternative")
        msg["From"] = self.sender
        msg["Subject"] = self.prefix + subject or "A Message for you"

        if to:
            if isinstance(to, list):
                to = ", ".join(to)
            msg["To"] = to

        if text is not None:
            msg.attach(MIMEText(text, "plain"))
        if html is not None:
            msg.attach(MIMEText(html, "html"))

        return msg

    def send_html(self, to: Union[AnyStr, List], msg: MIMEMultipart):
        """
        Send an email with HTML content.

        :param to: A list of target email addresses
        :type to: Union[AnyStr, List]
        :param msg: The composed email message
        :type msg: MIMEMultipart
        :raises ValueError: Invalid type for to or msg
        :raises ConfigError: Sender does not have permission on the server"
        :raises SmtpToInvalid: One or more requested target email address(es) were
            rejected by the server
        """

        if isinstance(to, str):
            to = to.split(",")
        if not isinstance(to, list):
            raise ValueError(f"'to' should be a string or list, got {type(to)}")
        if not isinstance(msg, MIMEMultipart):
            raise ValueError(f"expected MIMEMultipart for msg got {type(msg)}")

        self.connect()
        if msg["To"] is None:
            msg["To"] = to
        try:
            logger.debug(f"Trying to send email to {to}")
            self.__conn.sendmail(self.sender, to, msg.as_string())
        except smtplib.SMTPSenderRefused as e:
            logger.exception("Sender does not have permission to send emails")
            raise ConfigError("Sender does not have permission on the server") from e
        except smtplib.SMTPRecipientsRefused as e:
            errors = []
            for u in to:
                errors.append(
                    f"Code: {e.recipients[u][0]}, Message: {e.recipients[u][1]}"
                )
            e_str = "\n\t".join(errors)
            logger.exception(
                f"Send email failed with the following errors: \n\t{e_str}"
            )
            raise SmtpToInvalid(f"Received the following errors: \n\t{e_str}")

        self.close()

    def send(self, to: Union[AnyStr, List], msg: str, subject: str):
        """
        Send an email message to the target recipient(s)

        :param to: A list of target email addresses
        :type to: Union[AnyStr, List]
        :param msg: The body of the email
        :type msg: str
        :param subject: Subject line
        :type subject: str
        :raises ValueError: Invalid to type
        :raises ConfigError: Authentication with the server failed
        :raises SmtpToInvalid: One or more requested target email address(es) were
            rejected by the server
        """

        if isinstance(to, str):
            to = to.split(",")
        if not isinstance(to, list):
            raise ValueError(f"'to' should be a string or list, got {type(to)}")
        email = EmailMessage()
        email.set_content(msg)
        email["Subject"] = self.prefix + subject
        email["To"] = to
        email["From"] = self.sender

        self.connect()
        try:
            logger.debug(f"Trying to send email to {to}")
            self.__conn.send_message(email, self.sender, to)
        except smtplib.SMTPSenderRefused as e:
            logger.exception("sender does not have permission to send emails")
            raise ConfigError("Sender does not have permission on the server") from e
        except smtplib.SMTPRecipientsRefused as e:
            errors = []
            for u in to:
                errors.append(
                    f"Code: {e.recipients[u][0]}, Message: {e.recipients[u][1]}"
                )
            e_str = "\n\t".join(errors)
            logger.exception(f"Send email failed with the following errors \n\t{e_str}")
            raise SmtpToInvalid(f"Received the following errors \n\t{e_str}")

        self.close()
