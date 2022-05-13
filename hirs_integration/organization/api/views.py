# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.routers import APIRootView

from . import serializers

from organization import models

class OrganizationRootView(APIRootView):
    def get_view_name(self):
        return 'Organization'


class OrganizationS2RootView(APIRootView):
    def get_view_name(self):
        return 'Organization Select2'


class S2BusinessUnitView(Select2ViewSet):
    queryset = models.BusinessUnit.objects.filter(is_deleted=False)
    serializer_class = serializers.S2BusinessUnitSerializer


class BusinessUnitView(ModelViewSet):
    queryset = models.BusinessUnit.objects.filter(is_deleted=False)
    serializer_class = serializers.BusinessUnitSerializer


class S2JobRoleView(Select2ViewSet):
    queryset = models.JobRole.objects.filter(is_deleted=False)
    serializer_class = serializers.S2JobRoleSerializer


class JobRoleView(ModelViewSet):
    queryset = models.JobRole.objects.filter(is_deleted=False)
    serializer_class = serializers.JobRoleSerializer


class S2LocationView(Select2ViewSet):
    queryset = models.Location.objects.filter(is_deleted=False)
    serializer_class = serializers.S2LocationSerializer


class LocationView(ModelViewSet):
    queryset = models.Location.objects.filter(is_deleted=False)
    serializer_class = serializers.LocationSerializer


class GroupMappingView(ModelViewSet):
    queryset = models.GroupMapping.objects.all()
    serializer_class = serializers.GroupMappingSerializer