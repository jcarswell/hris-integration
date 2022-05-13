# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.routers import APIRootView

from . import serializers
from smtp_client import models

class SMTPRootView(APIRootView):
    def get_view_name(self):
        return 'SMTP Client'


class SMTPS2RootView(APIRootView):
    def get_view_name(self):
        return 'SMTP Client Select2'


class S2EmailTemplateView(Select2ViewSet):
    queryset = models.EmailTemplates.objects.all()
    serializer_class = serializers.S2EmailTemplateSerializer


class EmailTemplateView(ModelViewSet):
    queryset = models.EmailTemplates.objects.all()
    serializer_class = serializers.EmailTemplateSerializer