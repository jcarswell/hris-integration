# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.validators import import_validator, ValidationError
from django.utils.translation import gettext_lazy as _t

__all__ = ("employee_fields",)

employee_fields = [
    (None, ""),
    ("first_name", _t("First Name")),
    ("middle_name", _t("Middle Name")),
    ("last_name", _t("Last Name")),
    ("suffix", _t("Suffix")),
    ("source_first_name", _t("Given First Name")),
    ("source_middle_name", _t("Given Middle Name")),
    ("source_last_name", _t("Given Last Name")),
    ("designations", _t("Designations")),
    ("title", _t("Title")),
    ("phone", _t("Phone Number")),
    ("address", _t("Address")),
    ("location", _t("Location")),
    ("status", _t("Status")),
    ("photo", _t("Photo")),
    ("id", _t("Employee ID")),
    ("bu", _t("Business Unit Name")),
    ("bu_id", _t("Business Unit ID")),
    ("manager", _t("Manager")),
    ("username", _t("Username")),
    ("upn", _t("User Principal Name")),
    ("email_address", _t("Email Address")),
    ("is_supervisor", _t("Is Supervisor")),
    ("employeetype", _t("Employee Type")),
    ("manager_id", _t("Manager ID")),
]
