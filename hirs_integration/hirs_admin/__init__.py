from .apps import HirsAdminConfig

__all__ = ('HirsAdminConfig','setup')

def setup():
    from .helpers import config
    config.configuration_fixures()