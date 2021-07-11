from .apps import AdExportConfig

__all__ = ("setup","run","AdExportConfig")

def setup():
    from .helpers import config
    from cron.helpers.job_manager import Job
    config.configuration_fixures()
    cj = Job('ad_export','ad_export.run','10 */6 * * *')
    cj.save()

def run(full=False):
    from .ad_export import Export
    Export(full).run()