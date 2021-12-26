from .apps import SmtpClientConfig
from .exceptions import SmtpServerError,SmtpToInvalid,ConfigError

__all__ = ('SmtpClientConfig','setup','SmtpServerError','SmtpToInvalid')

def setup():
    """No setup task required for this module"""
    pass