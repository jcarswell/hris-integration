# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import logging

from django.db import models
from django.utils.translation import gettext_lazy as _t

logger = logging.getLogger('employee.models.base')


class EmployeeState(models.Model):
    """Defined the possible states of an employee"""

    STATE_TERM = 'terminated'
    STATE_ACT = 'active'
    STATE_LEA = 'leave'

    status_choices = [
        (STATE_TERM, _t('Terminated')),
        (STATE_ACT, _t('Active')),
        (STATE_LEA, _t('Leave')),
        ]
    
    class Meta:
        abstract = True

    state = models.BooleanField(default=True)
    leave = models.BooleanField(default=False)

    @property
    def status(self):
        if self.state and self.leave:
            return self.STAT_LEA
        elif self.state:
            return self.STAT_ACT
        else:
            return self.STAT_TERM

    @status.setter
    def status(self,new_status):
        logger.debug(f"setting new status {new_status}")
        if isinstance(new_status,(bool,int)):
            self.leave = not bool(new_status)
            self.state = bool(new_status)
        elif isinstance(new_status,str) and new_status.lower() in [self.STATE_ACT,self.STATE_LEA,self.STATE_TERM]:
            if new_status.lower() == self.STAT_LEA:
                logger.debug(f"Setting to Leave")
                self.leave = True
                self.state = True
            elif new_status.lower() == self.STAT_TERM:
                logger.debug(f"Setting to Terminated")
                self.leave = True
                self.state = False
            elif new_status.lower() == self.STAT_ACT:
                logger.debug(f"Setting to Active")
                self.leave = False
                self.state = True

