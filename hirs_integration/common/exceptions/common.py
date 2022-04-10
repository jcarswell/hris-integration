# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.exceptions import HrisIntegrationBaseError


class CommonError(HrisIntegrationBaseError):
    """The base exception for which all common exceptions are derived."""


class FixturesError(CommonError):
    """Error thrown during installation or retrival of fixtures"""


class SettingsError(CommonError):
    """Error thrown when there is an issue with the settings data"""