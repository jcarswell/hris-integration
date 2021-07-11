from django.db.models import Model

class BaseException(Exception):
    pass


class AlreadyExists(BaseException):
    """The specified job already exists"""
    pass


class ModuleOrMethodInvalid(BaseException):
    """The defined path does not match a valid path or function"""
    pass