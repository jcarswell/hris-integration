# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from hris_integration.api.viewsets import Select2ViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.routers import APIRootView
from rest_framework.serializers import ValidationError

from . import serializers
from user_applications import models

logger = logging.getLogger("user_applications.api.views")


class UserApplicationsRootView(APIRootView):
    def get_view_name(self):
        return "User Applications"


class UserApplicationsS2RootView(APIRootView):
    def get_view_name(self):
        return "User Applications Select2"


class S2Software(Select2ViewSet):
    queryset = models.Software.objects.all()
    serializer_class = serializers.s2SoftwareSerializer
    filterset_fields = ["name", "licensed"]


class Software(ModelViewSet):
    queryset = models.Software.objects.all()
    serializer_class = serializers.SoftwareSerializer
    read_only_fields = ["id"]
    filterset_fields = ["name", "licensed"]
    permission_classes = [DjangoModelPermissions | IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        for employee in instance.employees.all():
            models.Account.objects.create(employee=employee, software=instance)

    def perform_update(self, serializer):
        employees = []
        if serializer.instance:
            if (
                serializer.validated_data
                and serializer.validated_data.get("licensed", False)
                != serializer.instance.licensed
                and serializer.validated_data.get("licensed", False) == True
                or serializer.validated_data.get("max_users", 0)
                != serializer.instance.max_users
                and serializer.validated_date.get("max_users", 0) > 0
            ):
                for account in models.Account.objects.filter(
                    software=serializer.instance
                ):
                    employees.append(account.employee)
            else:
                employees = None
            if serializer.validated_data.get(
                "max_users", serializer.instance.max_users
            ) > len(employees):
                raise ValidationError(
                    f"There are currently {len(employees)} employees using this"
                    " software. Which is more than the maximum allowed users."
                )
            else:
                instance = serializer.save()
                if employees:
                    for employee in employees:
                        instance.employees.add(employee)
                    instance.save()
                elif employees is None:
                    for employee in instance.employees.all():
                        instance.employees.remove(employee)
                    instance.save()
        else:
            raise ValidationError(
                "In perform update Software and serializer instance is None"
            )


class S2Account(Select2ViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.S2AccountSerializer
    filterset_fields = ["software", "employee", "expire_date"]


class Account(ModelViewSet):
    queryset = models.Account.objects.all()
    serializer_class = serializers.AccountSerializer
    read_only_fields = ["id"]
    permission_classes = [DjangoModelPermissions | IsAuthenticated]
    filterset_fields = ["software", "employee", "expire_date"]

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.employee and instance.software:
            if instance.software.licensed or instance.software.max_users:
                instance.software.employees.add(instance.employee)

    def perform_destroy(self, instance):
        try:
            instance.software.employees.remove(instance.employee)
        except Exception:
            logger.debug("Could not remove employee from software.")
        instance.delete()
