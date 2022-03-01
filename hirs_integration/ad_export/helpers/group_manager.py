import logging

from pyad import ADGroup
from hirs_admin.models import GroupMapping
from hirs_admin import validators

logger = logging.getLogger('ad_export.GroupManager')

class GroupManager:
    def __init__(self,job,bu,location):
        self.add_groups = []
        self.remove_groups = []
        all_groups = GroupMapping.objects.all()
        
        for group in all_groups:
            if group.all:
                self._add(group.dn)

        self.get_jobs(all_groups,job)
        self.get_business_units(all_groups,bu)
        self.get_locations(all_groups,location)
        self.parse_config_groups()

    def get_jobs(self,groups,job):
        for group in groups:
            if self.__iter_group(group.jobs,job) and group.jobs_not == False:
                self._add(group.dn)
            elif self.__iter_group(group.jobs,job) and group.jobs_not == True:
                self._remove(group.dn)
            elif not self.__iter_group(group.jobs,job) and group.jobs_not == True:
                self._add(group.dn)

    def get_business_units(self,groups,business_unit):
        for group in groups:
            if self.__iter_group(group.bu,business_unit) and group.bu_not == False:
                self._add(group.dn)
            elif self.__iter_group(group.bu,business_unit) and group.bu_not == True:
                self._remove(group.dn)
            elif not self.__iter_group(group.bu,business_unit) and group.bu_not == True:
                self._add(group.dn)

    def get_locations(self,groups,location):
        for group in groups:
            if self.__iter_group(group.loc,location) and group.loc_not == False:
                self._add(group.dn)
            elif self.__iter_group(group.loc,location) and group.loc_not == True:
                self._remove(group.dn)
            elif not self.__iter_group(group.loc,location) and group.loc_not == True:
                self._add(group.dn)

    def _add(self,group):
        if group in self.remove_groups:
            logger.debug(f"Skipping _add for '{group}' as it exists in remove groups")
        elif group not in self.add_groups:
            logger.debug(f"Added group to add_groups: {group}")
            self.add_groups.append(group)

    def _remove(self,group):
        if group in self.add_groups:
            logger.debug(f"Removing '{group}' from add_groups")
            self.add_groups.pop(self.add_groups.index(group))
        
        if group not in self.remove_groups:
            logger.debug(f"Adding remove group: {group}")
            self.remove_groups.append(group)

    def parse_config_groups(self):
        """Parse config groups by dn or cn"""
        from .config import Config,EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_ADD
        config = Config()
        self.groups_leave = self.parse_group(config(EMPLOYEE_CAT,EMPLOYEE_LEAVE_GROUP_ADD))

    def parse_group(self,groups:str) -> list:
        output = []
        dn = []
        for group in groups.split(','):
            if len(group.split('=')) == 1:
                if dn != []:
                    output.append(dn.join(','))
                    dn = []
                try:
                    g = ADGroup.from_cn(group)
                    output.append(g.dn)
                except Exception as e:
                    logger.warning(f"{group} doesn't appear to be valid")
                    logger.debug(f"Caught exception while retrieving group: {e}")

            else:
                if group[0:2].lower() == "cn=":
                    if dn != []:
                        output.append(dn.join(','))
                        dn = []
                    dn.append(group)
                else:
                    dn.append(group)
        
        #Ensure that we're not leaving a DN out of the output
        if dn != []:
            output.append(dn.join(','))

        #Check that we are only returning valid DN's
        for x in range(0,len(output)):
            try:
                validators.DnValidator(output[x])
            except validators.ValidationError:
                logger.warn(f"got invalid or incomplete DN: {output[x]}")
                output.pop(x)

        return output
    
    @staticmethod
    def __iter_group(set,value):
        for item in set.all():
            if item == value:
                return True
        return False