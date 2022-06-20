# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.exceptions import HrisIntegrationBaseError
from pyad.pyadexceptions import (
    noExecutedQuery,
    invalidResults,
    InvalidAttribute,
    InvalidObjectException,
    noObjectFoundException,
    invalidOwnerException,
    win32Exception,
    genericADSIException,
    comException,
)


class ActiveDirectoryError(HrisIntegrationBaseError):
    pass


class TooManyResults(ActiveDirectoryError):
    def __init__(self, *args: object, result_count: int = None) -> None:
        self.result_count = result_count
        super().__init__(*args)
