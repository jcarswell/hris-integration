# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from .exceptions import ConfigError

__all__ = ("setup", "run", "ConfigError")


def setup():
    from cron.helpers.job_manager import Job

    cj = Job("corepoint_export")
    cj.new("corepoint_export.run", "0 4 * * *")


def run(full=False):
    from .helpers import config
    from .form import BaseExport
    import importlib

    modelclass = importlib.import_module(
        config.Config()(config.CAT_CONFIG, config.CONFIG_MODEL_FORM)
    )
    if hasattr(modelclass, "form") and isinstance(modelclass.form(), BaseExport):
        modelclass.form(not full).run()
    else:
        raise ConfigError(
            "configured form does not appear to be a valid module. Please Ensure"
            " that it's extending form.BaseExport and the form attrib is defined"
        )
