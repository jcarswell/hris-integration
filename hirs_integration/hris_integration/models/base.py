from django.db import models


class ChangeLogMixin(models.Modes):

    class Meta:
        abstract = True

    updated_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    