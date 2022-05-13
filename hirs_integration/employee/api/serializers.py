# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.serializers import Select2Serializer,Select2Meta
from rest_framework.serializers import ModelSerializer

from employee import models

class S2PhoneSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.Phone
        field_id = 'id'
        field_text = ['number']


class PhoneSerializer(ModelSerializer):
    class Meta:
        model = models.Phone
        fields = '__all__'


class S2AddressSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.Address
        field_id = 'id'
        field_text = ['address','city','province']


class AddressSerializer(ModelSerializer):
    class Meta:
        model = models.Address
        fields = '__all__'


class S2EmployeeSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.Employee
        field_id = 'id'
        field_text = ['first_name','last_name']


class EmployeeSerializer(ModelSerializer):
    class Meta:
        model = models.Employee
        fields = '__all__'
        read_only_fields = ['id','is_imported','is_export_ad','guid','password']


class S2EmployeeImportSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.EmployeeImport
        field_id = 'id'
        field_text = ['id','first_name','last_name']
        field_text_format = "{id}: {first_name} {last_name}"


class  EmployeeImportSerializer(ModelSerializer):
    class Meta:
        model = models.EmployeeImport
        fields = '__all__'
        read_only_fields = ['id','employee','is_matched']