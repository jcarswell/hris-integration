# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import models
from .manager import InactiveManager


class ChangeLogMixin(models.Model):
    """
    Generic Change Log Mixin that adds the created and updated on date fields.
    This will also add a change log to the change tracking table."""

    class Meta:
        abstract = True

    #: The date and time the record was last updated.
    updated_on: "datetime.datetime" = models.DateTimeField(
        auto_now_add=True, null=True, blank=True
    )
    #:  The date and time the record was created.
    created_on: "datetime.datetime" = models.DateTimeField(
        auto_now=True, null=True, blank=True
    )


class InactiveMixin(models.Model):
    """Defines a common set of fields to enable de-activation and soft-deleting"""

    class Meta:
        abstract = True

    objects = InactiveManager()

    #: Whether the object is active or not
    is_inactive: bool = models.BooleanField(default=False)
    #: Whether the object is soft-deleted or not
    is_deleted: bool = models.BooleanField(default=False)
