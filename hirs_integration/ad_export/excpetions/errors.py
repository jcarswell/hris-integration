class BaseException(Exception):
    pass


class ADResultsError(BaseException):
    """The specified job already exists"""
    pass

class UserDoesNotExist(BaseException):
    """The Request user doesn't exist"""
    pass