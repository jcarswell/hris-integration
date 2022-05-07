# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.models import ChangeLogMixin
from django.db import models

class Notification(ChangeLogMixin):
    """System Generated Notifications"""

    INFO = 3
    WARN = 2
    WARNING = 2
    ERROR = 1
    CRITICAL = 0

    #: list: the list of possible notification levels
    levelchoices = [
        (0,'Critical'),
        (1,'Error'),
        (2,'Warning'),
        (3,'Info'),
    ]

    class Meta:
        db_table = 'notifications'

    #: id: The unique id of the notification
    id = models.AutoField(primary_key=True)
    #: str: The notification message
    message = models.CharField(max_length=512)
    #: int: The level of the notification (0-3)
    level = models.IntegerField(choices=levelchoices)
    #: bool: Is acknowledged
    is_acknowledged = models.BooleanField(default=False)
    #: bool: Is cleared
    is_cleared = models.BooleanField(default=False)
    #: str: The source of the notification
    source = models.CharField(max_length=256, null=True, blank=True)
    #: str: repr of the source
    source_repr = models.CharField(max_length=512, null=True, blank=True)
    #: int: Object id of the source
    source_id = models.IntegerField(null=True, blank=True)