import logging
import os
import subprocess

from jinja2 import Template

from .helpers import config
from .exceptions import ConfigError

logger = logging.getLogger('corepoint_export.form')

class BaseExport:
    CSV_FILENAME = 'export.csv'
    def __init__(self,delta=True) -> None:
        self.get_employees(delta)
        self.map = config.MapSettings()

        self.export_file = config.get_config(config.CONFIG_CAT,config.CONFIG_PATH) + self.CSV_FILENAME
        self.callable = (config.get_config(config.CONFIG_CAT,config.CONFIG_PATH) +
                      config.get_config(config.CONFIG_CAT,config.CONFIG_EXEC))

        if (not os.path.isdir(config.get_config(config.CONFIG_CAT,config.CONFIG_PATH)) or
            not os.path.isfile(self.callable)):
            logger.critical(f"Corepoint WebService Module is not availbe at {self.callable}")
            raise ConfigError("It appears that Corepoint web service module is not installed, please install it or check the config")

        self.generate_config()

    def get_employees(self,delta):
        if not delta:
            self.employees = config.get_employees(delta,False)
        else:
            self.employees = config.get_employees(delta)

    def generate_config(self):
        attribs = {
            'API_URL': config.get_config(config.CONFIG_CAT,config.CONFIG_URL),
            'PUBLIC_KEY': config.get_config(config.CONFIG_CAT,config.CONFIG_PUB_KEY),
            'CUSTOMER_TOKEN': config.get_config(config.CONFIG_CAT,config.CONFIG_TOKEN),
            'CUSTOMER_ID': config.get_config(config.CONFIG_CAT,config.CONFIG_ID),
            'EXPORT_PATH': self.CSV_FILENAME,
            'map_values': self.map
        }
        path = (config.get_config(config.CONFIG_CAT,config.CONFIG_PATH) +
                config.get_config(config.CONFIG_CAT,config.CONFIG_EXEC) + 
                '.config')
        
        j2 = Template('tempates/CorePointWebServiceConnector.exe.config.j2')
        with open(path, 'w') as f:
            f.write(j2.render(attribs))
        
    def run(self):
        """
        This Method must be must be defined in a sub class
        
        Avalible class configs are:
            self.map - A dictionary containing the configured export map values.
                Unless you are overriding the generate config, the values should be
                used as the csv feilds
            self.callable - The executable to be called to run the CorePoint Import
            self.export_file - The path at which the export file should be saved. 
                To change this value override the __init__ function
        """
        raise NotImplementedError

    def __del__(self):
        #Make sure that we clean up the export file from disk
        if os.path.isfile(self.export_file):
            os.remove(self.export_file)

class Export(BaseExport):
    def run(self):
        keys = []
        for key,value in self.map.items():
            if value:
                keys.append(value)
        with open(self.export_file, 'w') as output:
            output.write(",".join(keys))
            for employee in self.employees:
                line = []
                for key in keys:
                    line.append(str(getattr(employee,key,'')))
                output.write(",".join(line))
        
        subprocess.run(self.callable)

form = Export
