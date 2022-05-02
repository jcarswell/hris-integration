# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.serializers import Select2Serializer,Select2Meta
from rest_framework.serializers import ModelSerializer

from smtp_client import models

class S2EmailTemplateSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.EmailTemplates
        field_id = 'id'
        field_text = ['name']

class EmailTemplateSerializer(ModelSerializer):
    class Meta:
        model = models.EmailTemplates
        fields = '__all__'