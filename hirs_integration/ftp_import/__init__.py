from .exceptions import CSVParsingException,ConfigurationError,ObjectCreationError
from .apps import FTPImportConfig

__all__ = ('setup','run','FTPImportConfig','CSVParsingException','ConfigurationError','ObjectCreationError')

def setup():
    from .helpers import settings
    from cron.helpers.job_manager import Job
    settings.configuration_fixures()
    cj = Job('ftp_import','ftp_import.run','0 */6 * * *')
    cj.save()

def run():
    from .ftp import FTPClient
    FTPClient().run_import()