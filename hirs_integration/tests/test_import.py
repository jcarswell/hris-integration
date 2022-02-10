import json
import logging
import unittest
import time

from ftp_import.forms import form
from ftp_import import csv
from ftp_import.helpers.stats import Stats
from ftp_import import ObjectCreationError
from hirs_admin.models import CsvPending
from pathlib import Path
from warnings import warn

logger = logging.getLogger('test.csv_import')

class manual_import(form):
    def __init__(self,field_config,**kwargs):
        super().__init__(field_config,**kwargs)
        if hasattr(self, 'csv_pending'):
            self.csv_pending.givenname = kwargs['first_name']
            self.csv_pending.lastname = kwargs['last_name']
            self.csv_pending.save()
        else:
            warn(f'Stats test will fail as {self.employee_id} is already pending')

class CsvManual(csv.CsvImport):
    def add_data(self):
        for row in range(0,len(self.data)):
            try:
                manual_import(self.fields,**self.data[row])
            except ValueError as e:
                logger.error("Failed to save Employee refere to previous logs for more details")
                Stats.errors.append(f"Line: {row} - Error: {e}")
            except ObjectCreationError as e:
                logger.error("Caught exception while creating employee, failed to create referance object. Refer to above logs")
                Stats.errors.append(f"Line: {row} - Error: {e}")

class TestCSVImport(unittest.TestCase):
    def setUp(self):
        Stats.time_start = time.time()

    def test_base_import(self):
        FILE = 'employee_data.csv'
        path = str(Path(__file__).resolve().parent) + '\\' + FILE
        with open(path) as data:
            csv.CsvImport(data)
        Stats.files.append(FILE)

    def test_manual_import(self):
        FILE = 'employee_data2.csv'
        path = str(Path(__file__).resolve().parent) + '\\' + FILE
        with open(path) as data:
            CsvManual(data)
        Stats.files.append(FILE)

    def test_stats(self):
        Stats.time_end = time.time
        self.assertGreater(Stats.rows_processed,26)
        self.assertEquals(Stats.errors,1)
        self.assertTrue(4 <= len(Stats.pending_users) <= 5)

    def tearDown(self) -> None:
        logger.info(Stats())
        
        