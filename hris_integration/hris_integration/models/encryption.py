import logging

from typing import Any
from cryptography.fernet import Fernet
from django import conf
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _t

logger = logging.getLogger("hris_integration.FieldEncryption")


class FieldEncryption:
    def __init__(self) -> None:
        try:
            self.key = Fernet(conf.settings.ENCRYPTION_KEY)
        except Exception:
            raise ValueError(
                "Encryption key is not available, check SECRET_KEY and SALT"
            )

    def encrypt(self, data: str) -> str:
        if data == None:
            data = ""

        try:
            return self.key.encrypt(data.encode("utf-8")).decode("utf-8")
        except Exception as e:
            logger.critical("An Error occurred encrypting the data provided")
            raise ValueError(e) from e

    def decrypt(self, data: bytes) -> str:
        if data in (None, ""):
            return ""
        if not isinstance(data, bytes):
            data = data.encode("utf-8")

        try:
            return self.key.decrypt(data).decode("utf-8")
        except Exception as e:
            logger.critical("An Error occurred decrypting the data provided")
            raise ValueError(e) from e

    def is_encrypted(self, data: bytes) -> bool:
        if data in (None, ""):
            return False
        if not isinstance(data, bytes):
            data = data.encode("utf-8")

        try:
            self.key.decrypt(data)
            return True
        except Exception:
            return False


class PasswordField(CharField):
    description = _t("An encrypted password field")

    def __init__(self, *args, max_length=128, **kwargs):
        self.encrypt = FieldEncryption()
        if kwargs.get("primary_key", False):
            raise ValueError("PasswordField cannot be a primary key")
        super().__init__(*args, max_length=max_length, **kwargs)

    def to_python(self, value: str) -> str:
        """Decrypts the value

        :param value: an encrypted string
        :type value: str
        :return: the decrypted string or None if the value is not a password
        :rtype: str
        """
        if isinstance(value, str):
            if not self.encrypt.is_encrypted(value):
                return value
            return self.encrypt.decrypt(value)
        elif value is None:
            return None
        else:
            raise ValueError("Invalid value for PasswordField")

    def from_db_value(self, value: str, expression: Any, connection: Any) -> str:
        return self.to_python(value)

    def get_prep_value(self, value: str) -> str:
        if value == None:
            return value
        if self.encrypt.is_encrypted(value):
            return value
        return self.encrypt.encrypt(value)
