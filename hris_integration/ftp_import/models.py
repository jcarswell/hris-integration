# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import models


class FileTrack(models.Model):
    """Table to track which files have been imported already"""

    #: The name of the imported file.
    name: str = models.CharField(max_length=255, unique=True)
