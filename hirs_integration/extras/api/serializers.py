# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.serializers import Select2Serializer,Select2Meta
from rest_framework.serializers import ModelSerializer

from extras import models

class S2Countries(Select2Serializer):
    class Meta(Select2Meta):
        model = models.Country
        field_id = 'id'
        field_text = ['name']


class CountriesSerializer(ModelSerializer):
    class Meta:
        model = models.Country
        fields = '__all__'
        read_only_fields = ['id']


class S2StatesSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.State
        field_id = 'id'
        field_text = ['name']


class StatesSerializer(ModelSerializer):
    class Meta:
        model = models.State
        fields = '__all__'
        read_only_fields = ['id']