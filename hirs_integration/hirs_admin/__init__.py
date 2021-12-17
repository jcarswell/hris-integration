from .apps import HrisAdminConfig
from .exceptions import RenderError

__all__ = ('HrisAdminConfig','setup','RenderError')

def setup():
    from .helpers import config
    config.configuration_fixures()