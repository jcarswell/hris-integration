# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List
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
    level_choices: List[tuple] = [
        (0, "Critical"),
        (1, "Error"),
        (2, "Warning"),
        (3, "Info"),
    ]

    class Meta:
        db_table = "notifications"

    id = models.AutoField(primary_key=True)
    #: The notification message
    message: str = models.CharField(max_length=512)
    #: The level of the notification (0-3)
    level: int = models.IntegerField(choices=level_choices)
    #: Is acknowledged
    is_acknowledged: bool = models.BooleanField(default=False)
    #: Is cleared
    is_cleared: bool = models.BooleanField(default=False)
    #: The source of the notification
    source: str = models.CharField(max_length=256, null=True, blank=True)
    #: repr of the source
    source_repr: str = models.CharField(max_length=512, null=True, blank=True)
    #: Object id of the source
    source_id: int = models.IntegerField(null=True, blank=True)
