# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from .errors import ConfigError, SmtpServerError, SmtpToInvalid, InvalidTemplate

__all__ = ("ConfigError", "SmtpServerError", "SmtpToInvalid", "InvalidTemplate")
