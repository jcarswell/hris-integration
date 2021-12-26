class HrisIntegrationBaseError(Exception):
    """The base exception for which all hris_integration error are derived."""

class CommonError(HrisIntegrationBaseError):
    """The base exception for which all common exceptions are derived."""

class FixturesError(CommonError):
    """Error thrown during installation or retrival of fixtures"""

class SettingsError(CommonError):
    """Error thrown when there is an issue with the settings data"""
