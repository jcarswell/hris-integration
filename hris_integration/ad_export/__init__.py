# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from .apps import AdExportConfig
from .exceptions import ADResultsError, UserDoesNotExist, ConfigError, ADCreateError

__all__ = (
    "setup",
    "run",
    "AdExportConfig",
    "ADResultsError",
    "UserDoesNotExist",
    "ConfigError",
    "ADCreateError",
)


def setup():
    from cron.helpers.job_manager import Job

    cj = Job("ad_export", "ad_export.run", "10 */6 * * *")
    cj.save()


def run(full: bool = False) -> None:
    """
    Run the ad_export process using the configured export from from the configuration

    :param full: Run a Full export process or a delta sync, defaults to False
    :type full: bool, optional
    :raises ValueError: If the configured export form is not a subclass of
        ad_export.form.BaseExport
    :raises ConfigError: If the module is not valid
    """

    from .helpers import config
    from .form import BaseExport
    import importlib

    try:
        modelclass = importlib.import_module(
            config.get_config(config.CONFIG_CAT, config.CONFIG_IMPORT_FORM)
        )
        if not hasattr(modelclass, "form"):
            raise ConfigError(
                "The configured form does not appear to be a valid export module. Please "
                "ensure that the form attribute is defined and points to your form class."
            )
        if not issubclass(modelclass.form, BaseExport):
            raise ValueError("Form must be a subclass of BaseExport")

        form = modelclass.form(full)
    except ImportError:
        raise ConfigError(
            "The configured import form module '{}' does not exist".format(
                config.get_config(config.CONFIG_CAT, config.CONFIG_IMPORT_FORM)
            )
        )
    except TypeError:
        raise ConfigError("The configured import form module is not a valid module")

    form.run()
