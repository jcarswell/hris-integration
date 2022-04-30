# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet

from . import serializers
from smtp_client import models

class S2EmailTemplateView(Select2ViewSet):
    queryset = models.EmailTemplate.objects.all()
    serializer = serializers.S2EmailTemplateSerializer


class EmailTemplateView(ModelViewSet):
    queryset = models.EmailTemplate.objects.all()
    serializer_class = serializers.EmailTemplateSerializer