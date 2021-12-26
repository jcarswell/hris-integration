from common.exceptions import HrisIntegrationBaseError

class CronBaseError(HrisIntegrationBaseError):
    pass


class AlreadyExists(CronBaseError):
    """The specified job already exists"""
    pass


class ModuleOrMethodInvalid(CronBaseError):
    """The defined path does not match a valid path or function"""
    pass