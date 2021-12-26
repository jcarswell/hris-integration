from common.exceptions import HrisIntegrationBaseError

class CorepointExportBaseError(HrisIntegrationBaseError):
    pass


class ConfigError(CorepointExportBaseError):
    pass