from .apps import HrisAdminConfig

__all__ = ('HrisAdminConfig','setup')

def setup():
    from .helpers import config
    config.configuration_fixures()