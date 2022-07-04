# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.exceptions import HrisIntegrationBaseError

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