# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.validators import import_validator, ValidationError
from django.utils.translation import gettext_lazy as _t

__all__ = ("import_field_choices", "import_field_map_to")


def import_field_choices():
    from ftp_import.helpers.config import get_fields

    fields = {None: ""}
    fields.update(get_fields())
    for field in fields.keys():
        if field == None:
            yield ((None, ""))
        else:
            yield ((field, field))


import_field_map_to = [
    (None, ""),
    (
        "Employee Base Field",
        (
            ("id", _t("Employee ID")),
            ("start_date", _t("Start Date")),
            ("manager", _t("Manager")),
            ("first_name", _t("Given Name")),
            ("middle_name", _t("Middle Name")),
            ("last_name", _t("Surname")),
            ("suffix", _t("Suffix")),
            ("state", _t("State")),
            ("leave", _t("Leave State")),
            ("status", _t("Status")),
            ("type", _t("Employee Type")),
            ("username", _t("Username")),
            ("primary_job", _t("Primary Job")),
            ("secondary_jobs", _t("Secondary Job(s)")),
            ("location", _t("Location")),
            ("email_alias", _t("Email Alias")),
            ("password", _t("Password")),
        ),
    ),
    (
        "Phone Fields",
        (
            ("phone_label", _t("Phone Label")),
            ("number", _t("Phone Number")),
        ),
    ),
    (
        "Address Fields",
        (
            ("address_label", _t("Address Label")),
            ("street1", _t("Street Address 1")),
            ("street2", _t("Street Address 2")),
            ("street3", _t("Street Address 3")),
            ("province", _t("Province or State")),
            ("city", _t("City")),
            ("postal_code", _t("Zip or Postal Code")),
            ("country", _t("Country")),
        ),
    ),
]
