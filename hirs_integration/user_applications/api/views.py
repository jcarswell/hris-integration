# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.routers import APIRootView

from . import serializers
from user_applications import models

class UserApplicationsRootView(APIRootView):
    def get_view_name(self):
        return 'User Applications'


class UserApplicationsS2RootView(APIRootView):
    def get_view_name(self):
        return 'User Applications Select2'


class S2Software(Select2ViewSet):
    queryset = models.Software.objects.all()
    serializer_class = serializers.s2SoftwareSerializer
    filterset_fields = ['name','licensed']

class Software(ModelViewSet):
    queryset = models.Software.objects.all()
    serializer_class = serializers.SoftwareSerializer
    read_only_fields = ['id']
    filterset_fields = ['name','licensed']
    permission_classes = [DjangoModelPermissions|IsAuthenticated]


class S2Account(Select2ViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.S2AccountSerializer
    filterset_fields = ['software','employee','expire_date']


class Account(ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    read_only_fields = ['id']
    permission_classes = [DjangoModelPermissions|IsAuthenticated]
    filterset_fields = ['software','employee','expire_date']