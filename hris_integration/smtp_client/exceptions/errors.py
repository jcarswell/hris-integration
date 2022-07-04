# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.exceptions import HrisIntegrationBaseError
from django.core.exceptions import ObjectDoesNotExist


class SmtpClientBaseError(HrisIntegrationBaseError):
    pass


class ConfigError(SmtpClientBaseError):
    pass


class SmtpServerError(SmtpClientBaseError):
    pass


class SmtpToInvalid(SmtpClientBaseError):
    pass


class InvalidTemplate(SmtpClientBaseError, ObjectDoesNotExist):
    """The requested template does not exist"""

    template_name = None
