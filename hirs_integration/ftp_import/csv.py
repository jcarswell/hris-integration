import logging
import string
import importlib
import csv

from string import ascii_letters,digits

from .helpers import config
from .exceptions import ConfigurationError, ObjectCreationError

logger = logging.getLogger('ftp_import.CSVImport')

def decode(s) -> str:
    if isinstance(s,bytes):
        return s.decode('utf-8')
    elif isinstance(s,str):
        return s
    else:
        return str(s)

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
        #TODO: if self.import_errors -> send notification email

    def parse_headers(self, file_handle) -> None:
        import_fields = config.get_fields()
        
        # ensure we're at the start of the file to grab the header row
        file_handle.seek(0)
        
        headers = decode(file_handle.readline())
        logger.debug(f"parsing potentail header row {headers[0:60]}")
        #TODO: add text qualifier
        while headers[0] not in string.ascii_letters + string.digits:
            logger.debug("Discarding starting line(s) as it doesn't start with a valid character")
            logger.debug(f"line: {headers}")
            if headers[0] == self.sep:
                logger.error("The csv file doesn't seem to have a vaild header row or we discarded it")
                raise IndexError("The csv file does not seem to have a valid header row")
            headers = decode(file_handle.readline())
            logger.debug(f"parsing potentail header row {headers[0:60]}")

        new_fields = []
        for key in csv.reader([headers],delimiter=self.sep):
            key = self._safe(key)
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
        self.import_error = []
        data = csv.reader(file_handle, delimiter=self.sep)
        for row in data:
            row_data = {}
            if len(row) != len(self.fields):
                logger.error(f"Unable to parse employee {row[0]}")
                self.import_error.append(row[0])
            else:
                for x in range(len(self.fields)):
                    if self.fields[x] and self.fields[x]['import']:
                        row_data[self.fields[x]['field']] = row[x]

            self.data.append(row_data)

    @staticmethod
    def _safe(val:str) -> str:
        output = []
        for l in val:
            if l == ' ':
                output.append('_')
            elif l not in ascii_letters+digits:
                output.append('-')
            else:
                output.append(l.lower())
        
        return "".join(output)
        
    
    def add_data(self):
        try:
            form_module = importlib.import_module(self.form)
        except ModuleNotFoundError as e:
            logger.critical(f"failed to import configure form module {self.form}. Please ensure that the configured value is for a module not a class or function.")
            raise ConfigurationError(f"unable to import form lib {self.form}") from e
        
        if hasattr(form_module,'form'):
            form = form_module.form
        else:
            logger.critical(f"Form module has no attribute form")
            raise ConfigurationError(f"Form module has no attribute form")
        
        for row in self.data:
            try:
                form(self.fields,**row).save()
            except ValueError:
                logger.error("Failed to save Employee refere to previous logs for more details")
            except ObjectCreationError:
                logger.error("Caught exception while creating employee, failed to create referance object. Refer to above logs")
