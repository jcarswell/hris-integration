from .apps import SmtpClientConfig

__all__ = ('SmtpClientConfig','setup')

def setup():
    from .helpers import config
    config.configuration_fixures()