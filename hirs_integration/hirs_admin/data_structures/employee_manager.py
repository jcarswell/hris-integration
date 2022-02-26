from typing import Union
from django.db.models import Q
from hirs_admin.models import (Employee,EmployeePending,EmployeeOverrides,EmployeePhone,
                               EmployeeAddress,Location,GroupMapping)

class EmployeeManager:
    def __init__(self,emp_object:Union[Employee,EmployeePending]) -> None:
        if not isinstance(emp_object,(Employee,EmployeePending)):
            raise ValueError(f"expexted Employee or EmployeePending Object got {type(emp_object)}")

        self.config = Config()

        self.__qs_emp = emp_object
        self.merge = False
        if isinstance(self.__qs_emp,EmployeePending) and self.__qs_emp.employee and self.__qs_emp.guid:
            self.merge = True
            self.__emp_pend = emp_object
            self.__qs_emp = Employee.objects.get(emp_id=emp_object.employee.pk)
            self.pre_merge()
        self.get()

    def get(self):
        if isinstance(self.__qs_emp,Employee):
            self.__qs_over = EmployeeOverrides.objects.get(employee=self.__qs_emp)
            self.__qs_phone = EmployeePhone.objects.filter(employee=self.__qs_emp)
            self.__qs_addr = EmployeeAddress.objects.filter(employee=self.__qs_emp)
        else:
            self.__qs_over = self.__qs_emp
            self.__qs_phone = None
            self.__qs_addr = None

    def __str__(self) -> str:
        return str(self.__qs_emp)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}({repr(self.employee)})>"

    @property
    def employee(self) -> Employee:
        return self.__qs_emp

    @property
    def overrides(self) -> EmployeeOverrides:
        return self.__qs_over

    @property
    def designations(self) -> str:
        return self.__qs_over.designations

    @property
    def phone(self):
        if self.__qs_phone is None:
            return None

        for phone in self.__qs_phone:
            if phone.primary:
                return phone.number

        return None

    @property
    def address(self):
        if self.__qs_addr is None:
            return {}

        for addr in self.__qs_addr:
            if addr.primary or addr.lable.lower == "office":
                return addr

        return None

    @property
    def firstname(self) -> str:
        return self.__qs_over.firstname

    @property
    def lastname(self) -> str:
        return self.__qs_over.lastname

    @property
    def username(self) -> str:
        return self.__qs_emp.username

    @property
    def password(self) -> str:
        return self.__qs_emp.password

    @property
    def location(self) -> str:
        loc = self.__qs_over.location
        val = Location.objects.get(loc)
        return val.name

    @property
    def email_alias(self) -> str:
        return self.__qs_emp.email_alias

    @property
    def ou(self) -> str:
        return self.__qs_emp.primary_job.bu.ad_ou

    @property
    def title(self) -> str:
        return self.__qs_emp.primary_job.name

    @property
    def status(self) -> bool:
        return self.__qs_emp.status

    @property
    def photo(self) -> str:
        return self.__qs_emp.photo

    @property
    def id(self) -> int:
        return self.__qs_emp.emp_id

    def get_groups(self) -> list[str]:
        output = []
        #Positive group lookups
        gmaps = GroupMapping.objects.filter(Q(jobs=self.__qs_emp.primary_job.pk)&Q(jobs_not=False)|
                                            Q(bu=self.__qs_emp.primary_job.bu.pk)&Q(bu_not=False)|
                                            Q(loc=self.__qs_over.location.pk)&Q(loc_not=False)|
                                            Q(all=True))

        for group in gmaps:
            if group.dn not in output:
                output.append(group.dn)

        #Negitive group lookups
        gmaps = GroupMapping.objects.filter(Q(jobs=self.__qs_emp.primary_job.pk,_negated=True)&Q(jobs_not=True)|
                                            Q(bu=self.__qs_emp.primary_job.bu.pk,_negated=True)&Q(bu_not=True)|
                                            Q(loc=self.__qs_over.location.pk,_negated=True)&Q(loc_not=True))

        for group in gmaps:
            if group.dn not in output:
                output.append(group.dn)

        return output

    @property
    def bu(self):
        return self.__qs_emp.primary_job.bu.name

    @property
    def manager(self):
        try:
            return EmployeeManager(self.__qs_emp.manager or self.__qs_emp.primary_job.bu.manager)
        except Exception:
            return None

    @property
    def remove_groups(self) -> list[str]:
        output = self._leave_groups_del()

        gmaps = GroupMapping.objects.filter(Q(jobs=self.__qs_emp.primary_job.pk)&Q(jobs_not=True)|
                                            Q(bu=self.__qs_emp.primary_job.bu.pk)&Q(bu_not=True)|
                                            Q(loc=self.__qs_over.location.pk)&Q(loc_not=True))

        for group in gmaps:
            if group.dn not in output:
                output.append(group.dn)

        gmaps = GroupMapping.objects.filter(Q(jobs=self.__qs_emp.primary_job.pk,_negated=True)&Q(jobs_not=False)|
                                            Q(bu=self.__qs_emp.primary_job.bu.pk,_negated=True)&Q(bu_not=False)|
                                            Q(loc=self.__qs_over.location.pk,_negated=True)&Q(loc_not=False))

        for group in gmaps:
            if group.dn not in output:
                output.append(group.dn)

        return output

    @property
    def upn(self) -> str:
        return f'{self.email_alias}@{self.config(CONFIG_CAT,CONFIG_UPN)}'

    def clear_password(self) -> bool:
        if self.__qs_emp._password:
            self.__qs_emp.clear_password(True)
            return True
        else:
            return False

    @property
    def guid(self) -> str:
        if hasattr(self.__qs_emp,'guid'):
           return self.__qs_emp.guid
        else:
            return None

    @guid.setter
    def guid(self,id) -> None:
        if hasattr(self.__qs_emp,'guid'):
            self.__qs_emp.guid = id

    @property
    def pending(self):
        if isinstance(self.__qs_emp,EmployeePending):
            return True
        return False
