# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from .exceptions import CSVParsingException, ConfigurationError, ObjectCreationError
from .apps import FTPImportConfig

__all__ = (
    "setup",
    "run",
    "FTPImportConfig",
    "CSVParsingException",
    "ConfigurationError",
    "ObjectCreationError",
)


def setup():
    from cron.helpers.job_manager import Job

    cj = Job("ftp_import")
    cj.new("ftp_import.run", "0 */6 * * *")


def run():
    from .ftp import FTPClient

    FTPClient().run_import()
