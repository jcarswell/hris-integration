# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from .apps import SettingsConfig
from .exceptions import RenderError

__all__ = ('SettingsConfig','setup','RenderError')

def setup():
    """No setup tasks required for this module"""
    pass