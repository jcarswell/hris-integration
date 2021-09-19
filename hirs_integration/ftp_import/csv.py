import logging
import string
import importlib
import csv

from .helpers import config
from .helpers.stats import Stats
from .helpers.text_utils import safe,decode
from .exceptions import ConfigurationError, ObjectCreationError

logger = logging.getLogger('ftp_import.CSVImport')

class CsvImport():
    def __init__(self, file_handle) -> None:
        if not hasattr(file_handle,'readable'):
            try:
                _ = file_handle.readable()
            except ValueError:
                raise ValueError("expected open file handle")
        
        self.fields = []
        self.data = []
        self.sep = config.get_config(config.CAT_CSV,config.CSV_FIELD_SEP)
        self.form = config.get_config(config.CAT_CSV,config.CSV_IMPORT_CLASS)

        self.parse_headers(file_handle)
        self.parse_data(file_handle)
        self.add_data()

    def parse_headers(self, file_handle) -> None:
        import_fields = config.get_fields()
        
        # ensure we're at the start of the file to grab the header row
        file_handle.seek(0)
        
        headers = decode(file_handle.readline())
        logger.debug(f"parsing potentail header row {headers[0:60]}")

        while headers[0] not in string.ascii_letters + string.digits + "'" + '"':
            logger.debug("Discarding starting line(s) as it doesn't start with a valid character")
            logger.debug(f"line: {headers}")
            if headers[0] == self.sep:
                logger.error("The csv file doesn't seem to have a vaild header row or we discarded it")
                raise IndexError("The csv file does not seem to have a valid header row")
            headers = decode(file_handle.readline())
            logger.debug(f"parsing potentail header row {headers[0:60]}")

        new_fields = []
        for key in next(csv.reader([headers],delimiter=self.sep)):
            key = safe(key)
            logger.debug(f"Processing header key: {key}")
            if key not in import_fields:
                logger.info(f"Found new field in CSV File {key}")
                new_fields.append(key)
            elif key in import_fields:
                logger.debug("Feild exists and will be imported")
                #append the field config to the fields list
                self.fields.append(import_fields[key])
                #add the key name to the just added field dict
                self.fields[-1]['field'] = key

        if len(new_fields) > 0:
            #Add the new fields to the configuration and re re-run parse_headers 
            #TODO: Added some smart logic to try and parse feilds automagically
            conf = config.CsvSetting()
            conf.add(*new_fields)
            self.import_fields = conf.fields
            self.fields = []
            return self.parse_headers(file_handle)
        else:
            logger.debug(f"There are {len(self.fields)} headers in the file")

    def parse_data(self, file_handle):
        self.parse_error = []
        
        for row in file_handle:
            for vals in csv.reader([decode(row)]):
                row_data = {}
                if len(vals) != len(self.fields):
                    logger.debug(f"Headers: {len(self.fields)} This row: {len(vals)}")
                    logger.error(f"Unable to parse employee {vals[0]}")
                    Stats.errors.append(f"Unable to parse employee {vals[0]} - Incorrect number of fields")
                    self.parse_error.append(vals[0])
                else:
                    for x in range(len(self.fields)):
                        if self.fields[x] and self.fields[x]['import']:
                            row_data[self.fields[x]['field']] = vals[x]
                    #logger.debug(f"Parsed keys for row: {row_data.keys()}")
                    self.data.append(row_data)

    def add_data(self):
        try:
            form_module = importlib.import_module(self.form)
        except ModuleNotFoundError as e:
            logger.critical(f"failed to import configure form module {self.form}. Please ensure that the configured value is for a module not a class or function.")
            Stats.errors.append(f"Failed to import importer. Please check the configuration")
            raise ConfigurationError(f"unable to import form lib {self.form}") from e
        
        if hasattr(form_module,'form'):
            form = form_module.form
        else:
            logger.critical(f"Form module has no attribute form")
            raise ConfigurationError(f"Form module has no attribute form")
        
        for row in range(0,len(self.data)):
            try:
                #logger.debug(f"{type(self.data[row])} - {self.data[row]}")
                f = form(self.fields,**self.data[row])
                f.save()
            except ValueError as e:
                logger.error("Failed to save Employee refere to previous logs for more details")
                Stats.errors.append(f"Line: {row} - Error: {e}")
            except ObjectCreationError as e:
                logger.error("Caught exception while creating employee, failed to create referance object. Refer to above logs")
                Stats.errors.append(f"Line: {row} - Error: {e}")
