# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.utils.translation import gettext_lazy as _t
from django.forms.widgets import Select
from hris_integration.forms import Form, MetaBase
from extras import widgets
from active_directory import validators

from . import models


class GroupMapping(Form):
    """Group Mapping Model Form"""

    name = _t("Group Mappings to Jobs")
    list_fields = ["dn"]

    class Meta(MetaBase):
        model = models.GroupMapping
        widgets = {
            "dn": widgets.SelectPicker(
                choices=validators.ad_groups(),
                attrs={"data-live-search": "true", "data-style": "bg-white"},
            ),
            "all": widgets.CheckboxInput(attrs={"class": "form-control"}),
            "jobs_not": widgets.CheckboxInput(attrs={"class": "form-control"}),
            "business_unit_not": widgets.CheckboxInput(attrs={"class": "form-control"}),
            "location_not": widgets.CheckboxInput(attrs={"class": "form-control"}),
            "jobs": widgets.SelectPickerMulti(attrs={"class": "form-control"}),
            "business_unit": widgets.SelectPickerMulti(attrs={"class": "form-control"}),
            "location": widgets.SelectPickerMulti(attrs={"class": "form-control"}),
        }
        labels = {
            "dn": _t("AD Group"),
            "all": _t("All Employees"),
            "jobs": _t("Jobs"),
            "jobs_not": _t("Not"),
            "business_unit": _t("Business Units"),
            "business_unit_not": _t("Not"),
            "location": _t("Locations"),
            "location_not": _t("Not"),
        }
        classes = {
            "dn": "selectpicker",
        }


class JobRole(Form):
    """Job Role Model Form"""

    name = _t("Job Roles")

    class Meta(MetaBase):
        model = models.JobRole
        fields = ("id", "name", "business_unit", "seats")
        labels = {
            "id": _t("Job Number"),
            "name": _t("Job Name"),
            "business_unit": _t("Business Unit"),
            "seats": _t("Number of Seats"),
        }
        disabled = ("id",)
        classes = {
            "business_unit": "selectpicker",
        }
        required = ("id", "name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["business_unit"].widget.attrs.update(
            {"data-live-search": "true", "data-style": "bg-white"}
        )


class BusinessUnit(Form):
    """Business Unit Model Form"""

    name = _t("Business Unit")

    class Meta(MetaBase):
        model = models.BusinessUnit
        fields = ("id", "name", "parent", "ad_ou", "manager")
        widgets = {
            "ad_ou": Select(choices=validators.ad_ous()),
        }
        labels = {
            "id": _t("Number"),
            "name": _t("Name"),
            "parent": _t("Parent"),
            "ad_ou": _t("Active Directory Folder"),
            "manager": _t("Manager"),
        }
        disabled = ("id",)
        classes = {
            "manager": "selectpicker",
            "ad_ou": "selectpicker",
            "parent": "selectpicker",
        }
        required = ("id", "name", "ad_ou")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["manager"].widget.attrs.update(
            {"data-live-search": "true", "data-style": "bg-white"}
        )
        self.fields["ad_ou"].widget.attrs.update(
            {"data-live-search": "true", "data-style": "bg-white"}
        )
        self.fields["parent"].widget.attrs.update(
            {"data-live-search": "true", "data-style": "bg-white"}
        )


class Location(Form):
    """Location Model Form"""

    name = _t("Building")

    class Meta(MetaBase):
        model = models.Location
        fields = ("id", "name")
        labels = {"id": _t("Number"), "name": _t("Name")}
        disabled = ("id",)
        required = ("id", "name")
