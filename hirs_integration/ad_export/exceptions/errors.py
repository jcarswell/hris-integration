from common.exceptions import HrisIntegrationBaseError

class AdExportBaseError(HrisIntegrationBaseError):
    pass


class ADResultsError(AdExportBaseError):
    """The specified job already exists"""
    def __init__(self, *args, row_count:int =None) -> None:
        self.row_count = row_count
        super().__init__(*args)


class UserDoesNotExist(AdExportBaseError):
    """The Request user doesn't exist"""
    pass


class ConfigError(AdExportBaseError):
    """Raised when there is an issue with the configuration"""
    pass


class ADCreateError(AdExportBaseError):
    """Raised when creating and AD Object Fails"""
    pass