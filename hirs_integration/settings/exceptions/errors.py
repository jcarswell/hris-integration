# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.exceptions import HrisIntegrationBaseError


class SettingsBaseError(HrisIntegrationBaseError):
    pass


class RenderError(SettingsBaseError):
    """Thrown when the system encounters an error with rendering a
    portion of a page."""

    pass


class FixturesError(SettingsBaseError):
    """Error thrown during installation or retrieval of fixtures"""


class SettingsError(SettingsBaseError):
    """Error thrown when there is an issue with the settings data"""


class SetupError(SettingsBaseError, UnboundLocalError):
    """Error thrown when there is an issue with the setup data"""
