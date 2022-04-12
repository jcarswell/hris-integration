# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.db import models
from warnings import warn

class FileTrack(models.Model):
    """Table to track which files have been imported already"""
    name = models.CharField(max_length=255,unique=True)


class CsvPending(models.Model):
    class Meta:
        db_table = 'csv_pending'

    id = models.IntegerField(primary_key=True)
    givenname = models.CharField(max_length=96,blank=True)
    surname = models.CharField(max_length=96,blank=True)
    row_data = models.TextField()
    
    @property
    def firstname(self):
        return self.givenname

    @firstname.setter
    def firstname(self,val):
        self.givenname = val

    @property
    def lastname(self):
        return self.surname

    @lastname.setter
    def lastname(self,val):
        self.surname = val

    def __str__(self):
        return f"{self.emp_id} - {self.givenname} {self.surname}"

    @property
    def emp_id(self):
        """Legacy method to return the emp_id of the employee (DEPRECATED)"""
        warn("CsvPending.emp_id is deprecated, use CsvPending.id instead", DeprecationWarning)
        return self.id