# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import subprocess

from jinja2 import Environment, PackageLoader, select_autoescape
from django.conf import settings
from pathlib import Path

from .helpers import config
from .helpers.utils import CSVSafe
from .exceptions import ConfigError

logger = logging.getLogger("corepoint_export.form")


class BaseExport:
    """
    This module defines the class used to export the employee data to a csv file the
    pass that data to the CorePoint WebService module which will handle importing the
    data into CorePoint.

    The whole export process is managed via the settings interface, allowing for
    customizations as what CorePoint fields are populated, the file formatting and the
    configuration specifics of the CorePoint WebService module.

    CorePoint is a web based Occupational Health and Safety management system.
        https://corepointinc.com/

    The Export process is as follows:
        1. Class initialization:
            - Get the employees to export. This defaults to only changed employees (delta)
            - Pull the configuration data from the config module
            - Generate the config file for the CorePoint WebService module

        2. Run the export process (class.run())):
            - This is defined in the sub class but should follow something similar to:
                - generate the csv file and save it to self.export_file
                - call the Corepoint WebService module (self.callable)
                - if successful, set the last run date (self.set_last_run)

        3. Cleanup:
            - Remove the export file from disk (unless if debugging is enabled)
    """

    CSV_FILENAME = "export.csv"

    def __init__(self, delta=True) -> None:
        self.get_employees(delta)
        self.map = config.MapSettings()
        self.config = config.Config()

        self.export_file = Path(
            self.config(config.CAT_CONFIG, config.CONFIG_PATH), self.CSV_FILENAME
        ).resolve()
        self.callable = Path(
            self.config(config.CAT_CONFIG, config.CONFIG_PATH),
            self.config(config.CAT_CONFIG, config.CONFIG_EXEC),
        ).resolve()

        if not self.export_file.parent.exists() or not self.callable.exists():
            logger.critical(
                f"Corepoint WebService Module is not available at {self.callable}"
            )
            raise ConfigError(
                "It appears that Corepoint web service module is not installed, "
                "please install it or check the config"
            )

        self.generate_config()

    def get_employees(self, delta: bool) -> None:
        """
        populate the self.employees list with the employees to export

        :param delta: Is the export only the changed employees?
        :type delta: bool
        """
        if not delta:
            self.employees = config.get_employees(delta, False)
        else:
            self.employees = config.get_employees(delta)

    def generate_config(self) -> None:
        """
        Generate the config file that the CorePoint WebServices application will use
        to import the exported csv file.
        """

        env = Environment(
            loader=PackageLoader("corepoint_export", "templates"),
            autoescape=select_autoescape(["XML"]),
        )

        attribs = {
            "API_URL": self.config(config.CAT_CONFIG, config.CONFIG_URL),
            "PUBLIC_KEY": self.config(config.CAT_CONFIG, config.CONFIG_PUB_KEY),
            "CUSTOMER_TOKEN": self.config(config.CAT_CONFIG, config.CONFIG_TOKEN),
            "CUSTOMER_ID": self.config(config.CAT_CONFIG, config.CONFIG_ID),
            "EXPORT_PATH": self.config(config.CAT_CONFIG, config.CONFIG_PATH)
            + self.CSV_FILENAME,
            "map_values": self.map,
        }
        path = Path(
            self.config(config.CAT_CONFIG, config.CONFIG_PATH),
            self.config(config.CAT_CONFIG, config.CONFIG_EXEC) + ".config",
        ).resolve()

        j2 = env.get_template("CorePointWebServiceConnector.exe.config.j2")
        with open(path, "w") as f:
            f.write(j2.render(attribs))

    def run(self):
        """
        This Method must be must be defined in a sub class

        Available class configs are:
            self.map - A dictionary containing the configured export map values.
                Unless you are overriding the generate config, the values should be
                used as the csv fields
            self.callable - The executable to be called to run the CorePoint Import
            self.export_file - The path at which the export file should be saved.
                To change this value override the __init__ function
        """
        raise NotImplementedError

    @staticmethod
    def set_last_run():
        config.set_last_run()

    def __del__(self):
        """Make sure that we clean up the export file from disk"""

        if self.export_file.exists() and not settings.DEBUG:
            self.export_file.unlink()


class Export(BaseExport):
    def run(self):
        """
        Parse the employees and generate the csv file, once it's done call the
        CorePoint executable.
        """

        logger.debug("Starting export")

        keys = []

        for key, value in self.map.items():
            if value:
                keys.append(CSVSafe().parse(value))

        logger.debug(f"Generating CSV file with fields: {keys}")

        if self.export_file.exists():
            self.export_file.unlink()

        with open(self.export_file, "w") as output:
            output.write(",".join(keys))
            output.write("\n")
            for employee in self.employees:
                line = []
                for key in keys:
                    line.append(CSVSafe().parse(getattr(employee, key, "")))
                output.write(",".join(line))
                output.write("\n")

        logger.debug(f"Starting CorePoint WebService Import with {self.callable}")
        subprocess.run(str(self.callable))
        logger.debug("CorePoint WebService Import Complete")

        self.set_last_run()


form = Export
