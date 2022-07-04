# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from .apps import SettingsConfig
from .exceptions import RenderError, FixturesError, SettingsError, SetupError

__all__ = (
    "SettingsConfig",
    "setup",
    "RenderError",
    "FixturesError",
    "SettingsError",
    "SetupError",
)


def setup():
    """Import all setting_fields from installed apps."""
    import logging

    from importlib import import_module
    from django.conf import settings
    from settings.config_manager import configuration_fixtures
    import sys

    logger = logging.getLogger("settings.setup")

    for app in settings.INSTALLED_APPS:
        try:
            module = import_module(app + ".helpers.settings_fields")
            logger.debug(f"Importing settings from {app}")
            configuration_fixtures(module.GROUP_CONFIG, module.CONFIG_DEFAULTS)
        except (ModuleNotFoundError, AttributeError):
            logger.warn(f"No settings_fields module found in {app}")
            pass
        except Exception as e:
            logger.exception(e)
            sys.exit(1)
