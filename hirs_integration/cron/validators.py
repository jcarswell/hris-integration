from django.core.exceptions import ValidationError

__all__ = ('cron_validator')

def cron_validator(value):
    try:
        from cron.helpers.data_structures import CronJob
        CronJob(value)
    except ValueError:
        ValidationError("string is not a valid cron string")