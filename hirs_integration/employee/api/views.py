# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.routers import APIRootView
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser, IsAuthenticated

from . import serializers
from employee import models

class EmployeeRootView(APIRootView):
    def get_view_name(self):
        return 'Employee'


class EmployeeS2RootView(APIRootView):
    def get_view_name(self):
        return 'Employee Select2'


class S2PhoneView(Select2ViewSet):
    queryset = models.Phone.objects.all()
    serializer_class = serializers.S2PhoneSerializer
    filterset_fields = ['employee','primary']


class PhoneView(ModelViewSet):
    queryset = models.Phone.objects.all()
    serializer_class = serializers.PhoneSerializer
    permission_classes = [DjangoModelPermissions|IsAuthenticated]
    filterset_fields = ['employee','primary']


class S2AddressView(Select2ViewSet):
    queryset = models.Address.objects.all()
    serializer_class = serializers.S2AddressSerializer
    filterset_fields = ['employee','primary','city','province','country']

class AddressView(ModelViewSet):
    queryset = models.Address.objects.all()
    serializer_class = serializers.AddressSerializer
    permission_classes = [DjangoModelPermissions|IsAuthenticated]
    filterset_fields = ['employee','primary','city','province','country']


class S2EmployeeView(Select2ViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.S2EmployeeSerializer
    filterset_fields = ['is_imported','is_exported_ad','start_date','nickname','state',
                        'leave','type','first_name','last_name','username',
                        'primary_job','location','manager','email_alias']


class EmployeeView(ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [DjangoModelPermissions]
    filterset_fields = ['is_imported','is_exported_ad','start_date','nickname','state',
                        'leave','type','first_name','last_name','username',
                        'primary_job','location','manager','email_alias']


class S2EmployeeImportView(Select2ViewSet):
    queryset = models.EmployeeImport.objects.all()
    serializer_class = serializers.S2EmployeeImportSerializer
    filterset_fields = ['is_matched','employee','state','leave','type',
                        'first_name','last_name','username','primary_job','location',
                        'manager','email_alias']


class EmployeeImportView(ModelViewSet):
    queryset = models.EmployeeImport.objects.all()
    serializer_class = serializers.EmployeeImportSerializer
    permission_classes = [IsAdminUser]
    filterset_fields = ['is_matched','employee','state','leave','type',
                        'first_name','last_name','username','primary_job','location',
                        'manager','email_alias']