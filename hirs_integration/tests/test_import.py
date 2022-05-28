# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import logging
import unittest
import time

from ftp_import.forms import form
from ftp_import import csv
from ftp_import.helpers.stats import Stats
from ftp_import import ObjectCreationError
from pathlib import Path
from employee.models import Employee

logger = logging.getLogger("test.csv_import")

employees = [
    {
        "first_name": "Josh",
        "last_name": "Kelly",
    },
    {
        "first_name": "Mitilda",
        "last_name": "Jacob",
    },
]


class manual_import(form):
    def save_post(self):
        from employee.models import Address, Phone

        if self.employee.is_matched:
            Address.objects.filter(employee=self.employee).delete()
            Phone.objects.filter(employee=self.employee).delete()
            self.employee.delete()
            self.employee.is_matched = False
            self.employee.save()


class PendingImport(csv.CsvImport):
    def add_data(self):
        for row in range(0, len(self.data)):
            try:
                manual_import(self.fields, **self.data[row])
            except ValueError as e:
                logger.error(
                    "Failed to save Employee refer to previous logs for more details"
                )
                Stats.errors.append(f"Line: {row} - Error: {e}")
            except ObjectCreationError as e:
                logger.error(
                    "Caught exception while creating employee, failed to create reference object. "
                    "Refer to above logs"
                )
                Stats.errors.append(f"Line: {row} - Error: {e}")


class TestCSVImport(unittest.TestCase):
    def setUp(self):
        Stats.time_start = time.time()

    def test_base_import(self):
        for employee in employees:
            Employee.objects.get_or_create(**employee)
        FILE = "employee_data.csv"
        path = str(Path(__file__).resolve().parent) + "\\" + FILE
        with open(path) as data:
            csv.CsvImport(data)
        Stats.files.append(FILE)

    def test_manual_import(self):
        FILE = "employee_data2.csv"
        path = str(Path(__file__).resolve().parent) + "\\" + FILE
        with open(path) as data:
            PendingImport(data)
        Stats.files.append(FILE)

    def test_stats(self):
        Stats.time_end = time.time
        self.assertGreater(Stats.rows_processed, 26)
        self.assertEquals(Stats.errors, 1)
        self.assertTrue(4 <= len(Stats.pending_users) <= 5)

    def tearDown(self) -> None:
        logger.info(Stats())
