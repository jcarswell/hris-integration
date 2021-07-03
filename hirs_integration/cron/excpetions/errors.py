class BaseException(Exception):
    pass

class AlreadyExists(BaseException):
    """The specified job already exists"""
    
class ModuleOrMethodInvalid(BaseException):
    """The defined path does not match a valid path or function"""