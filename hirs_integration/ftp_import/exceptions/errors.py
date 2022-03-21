# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

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