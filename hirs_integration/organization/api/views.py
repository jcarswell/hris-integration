from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet

from . import serializers

from organization import models

class S2BusinessUnitView(Select2ViewSet):
    queryset = models.BusinessUnit.objects.filter(is_delete=False)
    serializer = serializers.S2BusinessUnitSerializer


class BusinessUnitView(ModelViewSet):
    queryset = models.BusinessUnit.objects.filter(is_delete=False)
    serializer_class = serializers.BusinessUnitSerializer


class S2JobRoleView(Select2ViewSet):
    queryset = models.JobRole.objects.filter(is_delete=False)
    serializer = serializers.S2JobRoleSerializer


class JobRoleView(ModelViewSet):
    queryset = models.JobRole.objects.filter(is_delete=False)
    serializer_class = serializers.JobRoleSerializer


class S2LocationView(Select2ViewSet):
    queryset = models.Location.objects.filter(is_delete=False)
    serializer = serializers.S2LocationSerializer


class LocationView(ModelViewSet):
    queryset = models.Location.objects.filter(is_delete=False)
    serializer_class = serializers.LocationSerializer


class GroupMappingView(ModelViewSet):
    queryset = models.GroupMapping.objects.all()
    serializer_class = serializers.GroupMappingSerializer