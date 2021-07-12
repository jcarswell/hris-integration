import logging
import string
import importlib

from string import ascii_letters,digits

from .helpers import settings
from .exceptions import CSVParsingException,ConfigurationError

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
        self.sep = settings.get_config(settings.CSV_CONFIG,settings.CSV_FIELD_SEP)
        self.form = settings.get_config(settings.CSV_CONFIG,settings.CSV_IMPORT_CLASS)

        self.parse_headers(file_handle)
        self.parse_data(file_handle)
        self.add_data()

    def parse_headers(self, file_handle) -> None:
        import_fields = settings.get_fields()
        
        # ensure we're at the start of the file to grab the header row
        file_handle.seek(0)
        
        headers = file_handle.readline()
        while headers[0] not in string.ascii_letters + string.digits:
            logger.debug("Discarding starting line(s) as it doesn't start with a valid character")
            logger.debug(f"line: {headers}")
            if headers[0] == self.sep:
                logger.error("The csv file doesn't seem to have a vaild header row or we discarded it")
                raise IndexError("The csv file does not seem to have a valid header row")
            headers = file_handle.readline()

        new_fields = []
        for key in headers.split(self.sep):
            key =  self._safe(key)
            if key not in import_fields:
                logger.warning(f"found new field in CSV File {key}")
                new_fields.append(key)
            elif key in import_fields and import_fields[key]['import']:
                self.fields.append(import_fields[key])
                self.fields[-1]['field'] = key
                self.data[key] = []
            else:
                self.fields.append(None)

        if len(new_fields) > 0:
            #Add theh new fields to the configuration and re re-run parse_headers 
            #TODO: Added some smart logic to try and parse feilds automagically
            conf = settings.CsvSetting()
            conf.add(*new_fields)
            self.import_fields = conf.fields
            self.fields = []
            return self.parse_headers(file_handle)
    
    def parse_data(self, file_handle):
        for line in file_handle:
            line_data = line.split(self.sep)
            row_data = {}
            if len(line_data) != len(self.fields):
                raise CSVParsingException("Length of line is defferent than the header")

            for x in range(len(self.fields)):
                row_data[self.fields[x]['field']] = line_data[x]
                    
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
            form(self.fields,**row).save()
