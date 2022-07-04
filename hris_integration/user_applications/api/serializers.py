# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from hris_integration.api.serializers import Select2Serializer, Select2Meta
from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    ValidationError,
)
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from user_applications import models

logger = logging.getLogger("user_applications.api.serializers")


class s2SoftwareSerializer(Select2Serializer):
    class Meta(Select2Meta):
        model = models.Software
        field_id = "id"
        field_text = ["name"]


class SoftwareSerializer(ModelSerializer):
    class Meta:
        model = models.Software
        fields = "__all__"
        read_only_fields = ["id"]


class S2AccountSerializer(Select2Serializer):
    employee = PrimaryKeyRelatedField(queryset=models.Employee.objects.all())
    software = PrimaryKeyRelatedField(queryset=models.Software.objects.all())

    class Meta(Select2Meta):
        model = models.Account
        field_id = "id"
        field_text = ["software"]


class AccountSerializer(ModelSerializer):
    employee = PrimaryKeyRelatedField(
        queryset=models.Employee.objects.all(), required=True
    )
    software = PrimaryKeyRelatedField(
        queryset=models.Software.objects.all(), required=True
    )

    class Meta:
        model = models.Account
        fields = "__all__"
        read_only_fields = ["id"]
        depth = 1
        validators = [
            UniqueTogetherValidator(
                queryset=models.Account.objects.all(),
                fields=["employee", "software"],
                message="Account already exists for this employee.",
            )
        ]

    def validate_software(self, value):
        software = None
        if isinstance(value, (str, int)):
            software = models.Software.objects.get(id=int(value))
        elif isinstance(value, models.Software):
            software = value

        if (
            software.max_users
            and len(models.Account.objects.filter(software=software))
            >= software.max_users
        ):
            raise ValidationError("Software already has the maximum number of users.")

        return software
