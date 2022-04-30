# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.serializers import Select2Serializer,Select2Meta
from rest_framework.serializers import ModelSerializer

from user_applications import models

class s2SoftwareSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.Software
        field_id = 'id'
        field_text = ['name']


class SoftwareSerializer(ModelSerializer):
    class Meta:
        model = models.Software
        fields = '__all__'
        read_only_fields = ['id']


class S2EmployeeTrackedAccountSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.EmployeeTrackedAccount
        field_id = 'id'
        field_text = ['username']


class EmployeeTrackedAccountSerializer(ModelSerializer):
    class Meta:
        model = models.EmployeeTrackedAccount
        fields = '__all__'
        read_only_fields = ['id']