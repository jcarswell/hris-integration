# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
        logger.debug("converting source employee back to pending")
        if self.employee.is_matched and self.employee:
            e = Employee.objects.get(id=self.employee.employee.id)
            self.employee.employee = None
            self.employee.is_matched = False
            self.employee.save()
            e.delete()
            Stats.pending_users.append(str(self.employee))


class PendingImport(csv.CsvImport):
    def add_data(self):
        for row in range(0, len(self.data)):
            try:
                i = manual_import(self.fields, **self.data[row])
                i.save()
                Stats.rows_processed += 1
            except ValueError as e:
                logger.error(
                    "Failed to save Employee refer to previous logs for more details"
                )
                Stats.errors.append(f"Line: {row} - Error: {e}")
            except ObjectCreationError as e:
                logger.error(
                    f"Caught exception '{str(e)}' while creating employee, failed to create "
                    "reference object. Refer to above logs"
                )
                Stats.errors.append(f"Line: {row} - Error: {e}")
            except Exception as e:
                logger.debug(e)


class TestCSVImport(unittest.TestCase):
    def setUp(self):
        Stats.time_start = time.time()

    def test_base_import(self):
        pms = []
        for employee in employees:
            e, n = Employee.objects.get_or_create(**employee)
            if n:
                logger.debug(f"Created employee for import match test: {str(e)}")
                pms.append(repr(e))
        FILE = "employee_data.csv"
        path = str(Path(__file__).resolve().parent) + "\\" + FILE
        with open(path) as data:
            csv.CsvImport(data)
        Stats.files.append(FILE)
        for employee in pms:
            e = eval(employee)
            self.assertIsNotNone(e.employee_id)

    def test_manual_import(self):
        FILE = "employee_data2.csv"
        path = str(Path(__file__).resolve().parent) + "\\" + FILE
        with open(path) as data:
            PendingImport(data)
        Stats.files.append(FILE)

    def test_stats(self):
        self.assertGreater(Stats.rows_processed, 26)
        self.assertEqual(len(Stats.errors), 1)
        self.assertEqual(len(Stats.pending_users), 4)
        Stats.time_end = time.time()
        logger.info(Stats())
        logger.info("Warnings: \n" + "\n - ".join(Stats.warnings))
        logger.info("Errors: \n" + "\n - ".join(Stats.errors))
