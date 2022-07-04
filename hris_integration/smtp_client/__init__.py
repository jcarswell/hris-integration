# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from .apps import SmtpClientConfig
from .exceptions import SmtpServerError,SmtpToInvalid,ConfigError

__all__ = ('SmtpClientConfig','setup','SmtpServerError','SmtpToInvalid')

def setup():
    """No setup task required for this module"""
    pass