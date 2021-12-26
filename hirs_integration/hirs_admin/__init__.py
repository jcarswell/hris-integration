from .apps import HrisAdminConfig
from .exceptions import RenderError

__all__ = ('HrisAdminConfig','setup','RenderError')

def setup():
    """No setup tasks required for this module"""
    pass