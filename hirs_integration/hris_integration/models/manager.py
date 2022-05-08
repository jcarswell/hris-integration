from django.db.models import Manager

class InactiveManager(Manager):
    """Model manager that provides extra functionality for the InactiveMixin"""

    def get_queryset(self):
        """
        Overrides the default queryset to only return only objects that haven't
        been soft-deleted.
        """

        return super().get_queryset().filter(is_deleted=False)

    def all_objects(self):
        """Returns all objects, including soft-deleted"""
        return super().get_queryset()

    def inactive(self):
        """Returns all objects that are inactive"""
        return super().get_queryset().filter(is_inactive=True)

    def deleted(self):
        """Returns all objects that are soft-deleted"""
        return super().get_queryset().filter(is_deleted=True)