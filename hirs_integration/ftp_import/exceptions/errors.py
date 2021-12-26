from common.exceptions import HrisIntegrationBaseError

class FtpImportBaseError(HrisIntegrationBaseError):
    pass


class CSVParsingException(FtpImportBaseError):
    """ Raised when there is an issue with parsing the CSV File """
    pass


class ConfigurationError(FtpImportBaseError):
    """ Raised when the configuration provided is invalid """
    pass


class SFTPIOError(FtpImportBaseError):
    """ Rasied when their issues accessing files from the server """


class ObjectCreationError(FtpImportBaseError):
    """ Raised when there is an issue creating an object """
    pass