class BaseException(Exception):
    pass


class ADResultsError(BaseException):
    """The specified job already exists"""
    def __init__(self, *args, row_count:int =None) -> None:
        self.row_count = row_count
        super().__init__(*args)


class UserDoesNotExist(BaseException):
    """The Request user doesn't exist"""
    pass


class ConfigError(BaseException):
    """Raised when there is an issue with the configuration"""
    pass


class ADCreateError(BaseException):
    """Raised when creating and AD Object Fails"""
    pass