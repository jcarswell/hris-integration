# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from hris_integration.models import ChangeLogMixin, InactiveMixin
from warnings import warn


def get_default_ou() -> str:
    """Get the default organizational unit for new business units"""
    from organization.helpers.config import Config, GROUP_CONFIG, CONFIG_DEFAULT_OU

    try:
        return str(Config()(GROUP_CONFIG, CONFIG_DEFAULT_OU))
    except Exception:
        return ""


class BusinessUnit(MPTTModel, ChangeLogMixin, InactiveMixin):
    """The Business Units of the organization and the active directory
    organizational unit that is associated with the business unit.
    """

    class Meta:
        db_table = "business_unit"

    #: The ID of the Business Unit as defined by the organization
    id: int = models.IntegerField(primary_key=True)
    #: The name of the Business Unit
    name: str = models.CharField(max_length=128, null=False, blank=False)
    #: The parent Business Unit of the Business Unit. May be null.
    parent: "BusinessUnit" = TreeForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="business_unit_children",
    )
    #: The Active Directory organizational unit that is associated with the business unit
    ad_ou: str = models.CharField(max_length=256, default=get_default_ou)
    #: The Employee that is the manager of the Business Unit
    manager: "employee.models.Employee" = models.ForeignKey(
        "employee.Employee",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={"state": True},
    )

    def __str__(self) -> str:
        return self.name

    @property
    def bu_id(self) -> int:
        """Legacy ID field (DEPRECATED)"""
        warn(
            "BusinessUnit.bu_id is deprecated, use BusinessUnit.id instead",
            DeprecationWarning,
        )
        return self.id


class JobRole(ChangeLogMixin, InactiveMixin):
    """The Job roles of the organization"""

    class Meta:
        db_table = "job_role"

    #: The ID of the Job Role as defined by the organization
    id: int = models.IntegerField(verbose_name="Job ID", primary_key=True)
    #: The name of the Job Role
    name: str = models.CharField(max_length=255, verbose_name="Job Name")
    #: The Business Unit that the Job Role belongs to
    business_unit: BusinessUnit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Business Units",
    )
    #: The number of positions that are available for this Job Role
    seats: int = models.IntegerField(default=0, verbose_name="Seats")

    def __str__(self) -> str:
        return self.name

    @property
    def job_id(self) -> int:
        """Legacy ID field (Deprecated)"""
        warn("JobRole.job_id is deprecated, use JobRole.id instead", DeprecationWarning)
        return self.bu.id


class Location(MPTTModel, ChangeLogMixin, InactiveMixin):
    """The Locations of the organization"""

    class Meta:
        db_table = "location"

    #: The ID of the Location as defined by the organization
    id: int = models.IntegerField(
        primary_key=True,
    )
    #: The name of the Location
    name: str = models.CharField(
        max_length=128,
        null=False,
        blank=False,
    )
    #: The parent Location of the Location. May be null.
    parent: "Location" = TreeForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="location_children",
    )

    def __str__(self) -> str:
        return self.name

    def loc_id(self) -> int:
        """Legacy ID field (Deprecated)"""
        warn(
            "Location.loc_id is deprecated, use Location.id instead", DeprecationWarning
        )
        return self.id


class GroupMapping(ChangeLogMixin):
    """The Mapping table that defines the relationship between the AD groups and each
    of the defined job roles, business units, and locations.
    Each mapping has can either have a negative constraint or a positive constraint or
    be marked to apply to all employees.
    """

    class Meta:
        db_table = "group_mapping"

    #: The Distinguished Name of the Active Directory group
    dn: str = models.CharField(max_length=256)
    #: Whether the group applies to all employees
    all: bool = models.BooleanField(default=False)

    #: The Job Role that the group applies to
    jobs: JobRole = models.ManyToManyField(JobRole, blank=True)
    #: Negates the Job Role constraint
    jobs_not: bool = models.BooleanField(default=False)

    #: The Business Unit that the group applies to
    business_unit: BusinessUnit = models.ManyToManyField(BusinessUnit, blank=True)
    #: Negates the Business Unit constraint
    business_unit_not: bool = models.BooleanField(default=False)

    #: The Location that the group applies to
    location: Location = models.ManyToManyField(Location, blank=True)
    #: Negates the Location constraint
    location_not: bool = models.BooleanField(default=False)
