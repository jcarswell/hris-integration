# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoModelPermissions, IsAdminUser, IsAuthenticated

from . import serializers
from employee import models


class S2EmployeePhoneView(Select2ViewSet):
    queryset = models.EmployeePhone.objects.all()
    serializer = serializers.S2EmployeePhoneSerializer


class EmployeePhoneView(ModelViewSet):
    queryset = models.EmployeePhone.objects.all()
    serializer_class = serializers.EmployeePhoneSerializer
    permission_classes = [DjangoModelPermissions,IsAuthenticated]


class S2EmployeeAddressView(Select2ViewSet):
    queryset = models.EmployeeAddress.objects.all()
    serializer = serializers.S2EmployeeAddressSerializer


class EmployeeAddressView(ModelViewSet):
    queryset = models.EmployeeAddress.objects.all()
    serializer_class = serializers.EmployeeAddressSerializer
    permission_classes = [DjangoModelPermissions,IsAuthenticated]


class S2EmployeeView(Select2ViewSet):
    queryset = models.Employee.objects.all()
    serializer = serializers.S2EmployeeSerializer


class EmployeeView(ModelViewSet):
    queryset = models.Employee.objects.all()
    serializer_class = serializers.EmployeeSerializer
    permission_classes = [DjangoModelPermissions]


class S2EmployeeImportView(Select2ViewSet):
    queryset = models.EmployeeImport.objects.all()
    serializer = serializers.S2EmployeeImportSerializer


class EmployeeImportView(ModelViewSet):
    queryset = models.EmployeeImport.objects.all()
    serializer_class = serializers.EmployeeImportSerializer
    permission_classes = [IsAdminUser]