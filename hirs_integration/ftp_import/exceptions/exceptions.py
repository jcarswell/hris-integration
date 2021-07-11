class BaseException(Exception):
    pass


class CSVParsingException(BaseException):
    """ Raised when there is an issue with parsing the CSV File """
    pass


class ConfigurationError(BaseException):
    """ Raised when the configuration provided is invalid """
    pass


class SFTPIOError(BaseException):
    """ Rasied when their issues accessing files from the server """


class ObjectCreationError(BaseException):
    """ Raised when there is an issue creating an object """
    pass