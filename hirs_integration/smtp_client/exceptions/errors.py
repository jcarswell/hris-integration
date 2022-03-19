from common.exceptions import HrisIntegrationBaseError
from django.core.exceptions import ObjectDoesNotExist

class SmtpClientBaseError(HrisIntegrationBaseError):
    pass


class ConfigError(SmtpClientBaseError):
    pass


class SmtpServerError(SmtpClientBaseError):
    pass


class SmtpToInvalid(SmtpClientBaseError):
    pass


class InvlaidTemplate(SmtpClientBaseError,ObjectDoesNotExist):
    """The requested template does not exist"""
    template_name = None