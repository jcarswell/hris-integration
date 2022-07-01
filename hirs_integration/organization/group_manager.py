# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from pyad import ADGroup
from organization.models import GroupMapping
from common import validators

logger = logging.getLogger("ad_export.GroupManager")


class GroupManager:
    """
    The GroupManager represent all of the groups that are linked to an employee based on
    the employees job, business unit, and location. Optionally applications that are linked
    to an employee can be added via the add_application method.

    Once initialized the self.add_groups and self.remove_groups lists are populated with the
    relevant groups and the self.leave_groups list is populated with the groups that should
    be added when an employee is on leave and removed when the employee returns.
    """

    #: The groups to be added to the employee
    add_groups: list = []
    #: The groups to be removed from the employee
    remove_groups: list = []
    #: List of groups to be added when an employee is on leave
    groups_leave: list = []

    def __init__(
        self,
        job: "organization.models.JobRole",
        bu: "organization.models.BusinessUnit",
        location: "organization.models.Location",
    ) -> None:
        """
        Setup the GroupManager class

        :param job: The primary job of the employee
        :type job: organization.models.JobRole
        :param bu: The business unit that the employee belongs to
        :type bu: organization.models.BusinessUnit
        :param location: The location that the employee is located in
        :type location: organization.models.Location
        """

        self.add_groups = []
        self.remove_groups = []
        self.groups_leave = []
        all_groups = GroupMapping.objects.all()

        for group in all_groups:
            if group.all:
                self._add(group.dn)

        self.get_jobs(all_groups, job)
        self.get_business_units(all_groups, bu)
        self.get_locations(all_groups, location)
        self.parse_config_groups()

    def get_jobs(
        self, groups: "django.db.models.QuerySet", job: "organization.models.JobRole"
    ) -> None:
        """
        Parse the groups associated or explicitly not associated with the job role.

        :param groups: The queryset of groups to check against
        :type groups: django.db.models.QuerySet
        :param job: The job role to parse
        :type job: organization.models.JobRole
        """

        for group in groups:
            if self.__iter_group(group.jobs, job) and group.jobs_not == False:
                self._add(group.dn)
            elif self.__iter_group(group.jobs, job) and group.jobs_not == True:
                self._remove(group.dn)
            elif not self.__iter_group(group.jobs, job) and group.jobs_not == True:
                self._add(group.dn)

    def get_business_units(
        self,
        groups: "django.db.models.QuerySet",
        business_unit: "organization.models.BusinessUnit",
    ) -> None:
        """
        Parse the groups associated or explicitly not associated with the business unit.

        :param groups: The queryset of groups to check against
        :type groups: django.db.models.QuerySet
        :param business_unit: The business unit to parse
        :type business_unit: organization.models.BusinessUnit
        """

        for group in groups:
            if (
                self.__iter_group(group.business_unit, business_unit)
                and group.business_unit_not == False
            ):
                self._add(group.dn)
            elif (
                self.__iter_group(group.business_unit, business_unit)
                and group.business_unit_not == True
            ):
                self._remove(group.dn)
            elif (
                not self.__iter_group(group.business_unit, business_unit)
                and group.business_unit_not == True
            ):
                self._add(group.dn)

    def get_locations(
        self,
        groups: "django.db.models.QuerySet",
        location: "organization.models.Location",
    ) -> None:
        """
        Parse the groups associated or explicitly not associated with the location.

        :param groups: The queryset of groups to check against
        :type groups: django.db.models.QuerySet
        :param location: The location to parse
        :type location: organization.models.Location
        """

        for group in groups:
            if (
                self.__iter_group(group.location, location)
                and group.location_not == False
            ):
                self._add(group.dn)
            elif (
                self.__iter_group(group.location, location)
                and group.location_not == True
            ):
                self._remove(group.dn)
            elif (
                not self.__iter_group(group.location, location)
                and group.location_not == True
            ):
                self._add(group.dn)

    def add_application(self, app: "user_applications.models.Software") -> None:
        """
        If the application has a group mapping, add the group to the add_groups list

        :param app: The Software instance
        :type app: user_applications.models.Software
        """

        if app.mapped_group:
            logger.debug(f"Adding application {app.name}")
            self._add(app.mapped_group)

    def _add(self, group) -> None:
        """
        If the groups is not in the remove_groups list, add it to the add_groups list if
        it has not already been added.

        :param group: The group to add to the add_groups list
        :type group: str
        """

        if group in self.remove_groups:
            logger.debug(f"Skipping _add for '{group}' as it exists in remove groups")
        elif group not in self.add_groups:
            logger.debug(f"Added group to add_groups: {group}")
            self.add_groups.append(group)

    def _remove(self, group: str) -> None:
        """
        Ensure that the group is not in the add_groups list, and add it to the remove_groups
        list if it's not already in the list.

        :param group: The group to add to the remove_groups list
        :type group: str
        """

        if group in self.add_groups:
            logger.debug(f"Removing '{group}' from add_groups")
            self.add_groups.pop(self.add_groups.index(group))

        if group not in self.remove_groups:
            logger.debug(f"Adding remove group: {group}")
            self.remove_groups.append(group)

    def parse_config_groups(self) -> None:
        """Parse config groups by dn or cn"""

        from organization.helpers.config import Config, GROUPS_CAT, GROUPS_LEAVE_GROUP

        config = Config()
        self.groups_leave = self.parse_group(config(GROUPS_CAT, GROUPS_LEAVE_GROUP))

    def parse_group(self, groups: str) -> list:
        """
        Parse a string of groups into a list of groups and attempt to resolve non-dn strings
        to valid AD Groups.

        :param groups: String of groups to parse
        :type groups: str
        :return: The distinguished names for each parsed group
        :rtype: list
        """

        output = []
        dn = []
        logger.debug(f"parsing the following groups: {groups}")
        if not groups:
            return []

        for group in groups.strip("'\"").split(","):
            if group and len(group.split("=")) == 1:
                if dn != []:
                    output.append(",".join(dn))
                    dn = []
                try:
                    output.append(ADGroup.from_cn(group).dn)
                except Exception as e:
                    logger.warning(f"{group} doesn't appear to be valid")
                    logger.debug(f"Caught exception while retrieving group: {e}")

            else:
                if group[:3].lower() == "cn=":
                    if dn != []:
                        output.append(",".join(dn))
                        dn = []
                    dn.append(group)
                elif group:
                    dn.append(group)

        # Ensure that we're not leaving a DN out of the output
        if dn != []:
            output.append(",".join(dn))

        # Check that we are only returning valid DN's
        for x in range(0, len(output)):
            try:
                validators.DnValidator(output[x])
            except validators.ValidationError:
                logger.warn(f"got invalid or incomplete DN: {output[x]}")
                output.pop(x)

        return output

    @staticmethod
    def __iter_group(set: "django.db.models.QuerySet", value: str) -> bool:
        """
        Helper function to check if a value is in a django QuerySet.

        :param set: The QuerySet to check
        :type set: django.db.models.QuerySet
        :param value: the value to check for
        :type value: str
        :return: if the value exists in the set
        :rtype: bool
        """

        for item in set.all():
            if item == value:
                return True
        return False
