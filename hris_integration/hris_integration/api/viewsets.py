# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (
    IsAuthenticated,
    DjangoModelPermissions,
    BasePermission,
)


class NoAccess(BasePermission):
    """Deny all access to the view."""

    def has_permission(self, request, view):
        return False


class Select2ViewSet(ModelViewSet):
    """A limited viewset that provides get actions supporting the Select2 library."""

    def get_permissions(self):
        """Return the permissions for the viewset."""

        if self.action == "list":
            return [DjangoModelPermissions()]
        else:
            return [NoAccess()]
