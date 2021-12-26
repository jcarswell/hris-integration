from common.exceptions import HrisIntegrationBaseError

class SmtpClientBaseError(HrisIntegrationBaseError):
    pass


class ConfigError(SmtpClientBaseError):
    pass


class SmtpServerError(SmtpClientBaseError):
    pass

class SmtpToInvalid(SmtpClientBaseError):
    pass