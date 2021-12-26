class BaseException(Exception):
    pass


class ConfigError(BaseException):
    pass


class SmtpServerError(BaseException):
    pass

class SmtpToInvalid(BaseException):
    pass