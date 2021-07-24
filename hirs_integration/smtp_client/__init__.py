from .apps import SmtpClientConfig
from .exceptions import SmtpServerError,SmtpToInvalid

__all__ = ('SmtpClientConfig','setup','SmtpServerError','SmtpToInvalid')

def setup():
    from .helpers import config
    config.configuration_fixures()