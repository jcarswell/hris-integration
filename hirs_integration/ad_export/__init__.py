from .apps import AdExportConfig
from .exceptions import ADResultsError,UserDoesNotExist,ConfigError,ADCreateError

__all__ = ("setup","run","AdExportConfig","ADResultsError","UserDoesNotExist","ConfigError","ADCreateError")

def setup():
    from cron.helpers.job_manager import Job
    cj = Job('ad_export','ad_export.run','10 */6 * * *')
    cj.save()

def run(full=False):
    from .helpers import config
    from .form import BaseExport
    import importlib

    modelclass = importlib.import_module(config.get_config(config.CONFIG_CAT,config.CONFIG_IMPORT_FORM))
    if hasattr(modelclass,'form') and isinstance(modelclass.form(),BaseExport):
        modelclass.form(full).run()
    else:
        raise ConfigError("configured form does not appear to be a valid module. "\
                          "Please Ensure that it's extending form.BaseExport and the form attrib is defined")