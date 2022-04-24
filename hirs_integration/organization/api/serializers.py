# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.serializers import Select2Serializer,Select2Meta
from rest_framework.serializers import ModelSerializer

from organization import models

class S2BusinessUnitSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.BusinessUnit
        field_id = 'id'
        field_text = ['name']


class BusinessUnitSerializer(ModelSerializer):
    class Meta:
        model = models.BusinessUnit
        fields = '__all__'


class S2JobRoleSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.JobRole
        field_id = 'id'
        field_text = ['name']


class JobRoleSerializer(ModelSerializer):
    class Meta:
        model = models.JobRole
        fields = '__all__'


class S2LocationSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.Location
        field_id = 'id'
        field_text = ['name']


class LocationSerializer(ModelSerializer):
    class Meta:
        model = models.Location
        fields = '__all__'


class GroupMappingSerializer(ModelSerializer):
    class Meta:
        model = models.GroupMapping
        fields = '__all__'