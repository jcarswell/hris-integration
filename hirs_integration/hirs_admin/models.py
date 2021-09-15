import logging
import time
from django.core.exceptions import ValidationError

from django.db import models
from datetime import datetime
from cryptography.fernet import Fernet
from django import conf
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save,post_save
from random import choice
from django.utils.translation import gettext_lazy as _t
from string import ascii_letters, digits, capwords, ascii_uppercase,ascii_lowercase

logger = logging.getLogger('hirs_admin.Model')

# Helper Functions
def name_conflict(instance, name:str) -> bool:
    if instance._username == name or instance._email_alias:
        return False
    if (not Employee.objects.filter(_username=name).exists() and
            not Employee.objects.filter(_email_alias=name).exists() and
            not EmployeePending.objects.filter(_username=name).exists() and
            not EmployeePending.objects.filter(_email_alias=name).exists()):
        return False
    else:
        return True

def username_validator(first:str, last:str =None, suffix:str =None, allowed_char:list =None) -> str:
    """
    Username creation and valudation helper. Ensures that usernames are built using standard
    username rules and do not contain invalid characters.

    Args:
        first (str): Firstname or username/alias to be validate
        last (str, optional): lastname of the user
        suffix (str, optional): suffix for the username to ensure uniqueness
        allowed_char (list, optional): override the default list of invalid characters

    Returns:
        str: valid username or alias
    """
    invalid_char = ['!','@','#','$','%','^','&','*','(',')',
                    '_','+','=',';',':','\'','"',',','<','>',
                    ',',' ','`','~','{','}','|']
    substitue = ''
    suffix = suffix or ""
    if suffix == "0":
        suffix = ""
    allowed_char = allowed_char or []

    logger.debug(f"Validator got {first} {last} {suffix}")

    output = ''
    for x in first[0] + (last or first[1:]):
        if x in invalid_char and not x in allowed_char:
            output += substitue
        else:
            output += x

    logger.debug(f"validator username is {output} suffix is {suffix}")
    if suffix:
        return output[:19] + suffix
    else:
        return output[:20]

def upn_validator(first:str, last:str =None, suffix:str =None, allowed_char:list =None) -> str:
    """
    user principle name creation and valudation helper. Ensures that usernames are built using standard
    username rules and do not contain invalid characters.

    Args:
        first (str): Firstname or username/alias to be validate
        last (str, optional): lastname of the user
        suffix (str, optional): suffix for the username to ensure uniqueness
        allowed_char (list, optional): override the default list of invalid characters

    Returns:
        str: valid username or alias
    """
    invalid_char = ['!','@','#','$','%','^','&','*','(',')',
                    '_','+','=',';',':','\'','"',',','<','>',
                    ',',' ','`','~','{','}','|']
    substitue = ''
    suffix = suffix or ""
    if suffix == "0":
        suffix = ""
    allowed_char = allowed_char or []

    logger.debug(f"Validator got {first} {last} {suffix}")

    if last:
        upn = first + "." + last
    else:
        upn = first

    output = ''
    for x in upn:
        if x in invalid_char and not x in allowed_char:
            output += substitue
        else:
            output += x

    logger.debug(f"validator username is {output} suffix is {suffix}")
    return output + suffix

def set_username(instance, username:str =None) -> None:
    """Validate and set the username paramater

    Args:
        instance (Employee): Employee Model object
        username (str, optional): User defined username

    Raises:
        ValueError: Provided instance is not an Employee Model Object
        ValidationError: Unable to update the username
    """

    logger.debug(f"Setting username for {instance}")
    if isinstance(instance,EmployeeOverrides):
        # If we are using the EmployeeOverrides we need to ensure that we are
        # updating the employee table not the override table
        username = username_validator(instance.firstname,instance.lastname)
        set_username(instance.employee,username)
        instance.employee.save()
        return

    if not isinstance(instance,(Employee,EmployeePending)):
        raise ValueError("Only supported for Employee objects")

    if username:
        username = username_validator(username)
        if not name_conflict(instance,username):
            instance._username = username
            return
        else:
            raise ValidationError(f"{username} is already taken, failed to change username")

    username = username_validator(instance.givenname, instance.surname)

    base = username

    loop = 0
    while instance._username != username:
        if loop >= 10:
            logger.error("Something is wrong, unable to set user after 10 iters")
            raise ValidationError(f"unable to set username after 9 iterations")
        logger.debug(f"checking {username}")
        username = username_validator(base, suffix=str(loop))
        logger.debug(f"Validator returns {username}")
        if not name_conflict(instance,username):
            instance._username = username
        loop += 1

def set_upn(instance, upn:str =None) -> None:
    """
    Set the UPN/Email Alias for the EmployeeOverride model

    Args:
        instance (EmployeeOverrides): the Model instance for which we wil update

    Raises:
        ValueError: if the model is not EmployeeOverrides
        ValidationError: Unable to updated the upn
    """

    logger.debug(f"Setting upn for {instance}")
    if isinstance(instance, EmployeeOverrides):
        upn = upn or upn_validator(instance.firstname,instance.lastname)
        set_upn(instance.employee,upn)
        instance.employee.save()
        return

    if not isinstance(instance,(Employee,EmployeePending)):
        logger.debug(f'type recieved {type(instance)}')
        raise ValueError("Only supported for Employee objects")

    if upn:
        upn = upn_validator(upn)
        if not name_conflict(instance,upn):
            instance._email_alias = upn_validator(upn)
            return
        else:
            raise ValidationError(f"{upn} is already taken, failing to change upn")

    loop = 0

    while instance._email_alias != upn:
        if loop >= 10:
            logger.error("Something is wrong, unable to set user after 10 iters")
            raise ValidationError(f"unable to set upn after 9 iterations")
        logger.debug(f"Checking upn {upn}")
        if not name_conflict(instance,upn):
            instance._email_alias = upn
            break

        loop += 1
        upn = upn_validator(instance.firstname, instance.lastname, str(loop))

class FieldEncryption:
    def __init__(self) -> None:
        try:
            self.key = Fernet(conf.settings.ENCRYPTION_KEY)
        except Exception:
            raise ValueError("Encryption key is not available, check SECRET_KEY and SALT")
    
    def encrypt(self,data:str) -> str:
        if data == None:
            data = ''

        try:
            return self.key.encrypt(data.encode('utf-8')).decode('utf-8')
        except Exception as e:
            logger.critical("An Error occured encrypting the data provided")
            raise ValueError from e

    def decrypt(self,data:bytes) -> str:
        if not isinstance(data,bytes):
            data = data.encode('utf-8')

        try:
            return self.key.decrypt(data).decode('utf-8')
        except Exception as e:
            logger.critical("An Error occured decypting the data provided")
            raise ValueError from e

#######################
#####            ######
######  Models  #######
#####            ######
#######################

class SettingsManager(models.Manager):
    def get_by_path(self, group:str, catagory:str =None, item:str =None) -> QuerySet:
        path = group + Setting.FIELD_SEP

        if catagory:
            path = path + catagory + Setting.FIELD_SEP

        if item:
            path = path + item
            return self.filter(setting=path)

        return self.filter(setting__startswith=path)

class Setting(models.Model):
    """Application Settings"""
    FIELD_SEP = '/'
    class Meta:
        db_table = 'setting'
    setting = models.CharField(max_length=128,unique=True)
    _value = models.TextField(null=True,blank=True)
    hidden = models.BooleanField(default=False)
    
    o2 = SettingsManager()
    objects = o2

    @property
    def value(self) -> str:
        if self.hidden:
            return FieldEncryption().decrypt(self._value)
        else:
            return self._value
      
    @value.setter  
    def value(self, value:str) -> None:
        if value == None:
            value = ''
        if not isinstance(value,str):
            raise ValueError(f"Expected a str got {type(value)}")
        if self.hidden:
            self._value = FieldEncryption().encrypt(value)
        else:
            self._value = value

    def __str__(self):
        return f"{self.setting} - {self._value}"

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        """Ensure the the value is encrypted if the feild is set as hidden"""
        for char in instance.setting:
            if char not in ascii_letters + digits + instance.FIELD_SEP + '_-':
                instance.setting.replace(char,'_')
        if len(instance.setting.split(instance.FIELD_SEP)) != 3:
            raise ValueError("setting does not contain proper format, should be group/catagory/item")

    @staticmethod
    def _as_text(text:str) -> str:
        if _t(text) == text:
            text = " ".join(text.split("_"))
            return capwords(text)
        else:
            return _t(text)

    @property
    def group(self):
        return self.setting.split(self.FIELD_SEP)[0]

    @property
    def catagory(self):
        return self.setting.split(self.FIELD_SEP)[1]

    @property
    def item(self):
        return self.setting.split(self.FIELD_SEP)[2]

    @property
    def group_text(self):
        return self._as_text(self.setting.split(self.FIELD_SEP)[0])

    @property
    def catagory_text(self):
        return self._as_text(self.setting.split(self.FIELD_SEP)[1])

    @property
    def item_text(self):
        return self._as_text(self.setting.split(self.FIELD_SEP)[2])
pre_save.connect(Setting.pre_save, sender=Setting)


class BusinessUnit(models.Model):
    class Meta:
        db_table = 'businessunit'
    bu_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, null=False, blank=False, unique=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    ad_ou = models.CharField(max_length=256)
    manager = models.ForeignKey("Employee",null=True,blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class JobRole(models.Model):
    class Meta:
        db_table = 'jobroles'
    job_id = models.IntegerField(verbose_name="Job ID",primary_key=True)
    name = models.CharField(max_length=255,verbose_name="Job Name")
    bu = models.ForeignKey(BusinessUnit, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Business Units")
    seats = models.IntegerField(default=0, verbose_name="Seats")

    def __str__(self):
        return self.name


class Location(models.Model):
    class Meta:
        db_table = 'locations'
    bld_id = models.IntegerField(primary_key=True,)
    name = models.CharField(max_length=128, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    """ Employees Table """
    class Meta:
        db_table = 'employee'

    STAT_TERM = 'terminated'
    STAT_ACT = 'active'
    STAT_LEA = 'leave'

    emp_id = models.IntegerField(primary_key=True)
    created_on = models.DateField(null=False, blank=False, default=datetime.utcnow)
    updated_on = models.DateField(null=False, blank=False, default=datetime.utcnow)
    manager = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    givenname = models.CharField(max_length=96, null=False, blank=False)
    middlename = models.CharField(max_length=96, null=True, blank=True)
    surname = models.CharField(max_length=96, null=False, blank=False)
    suffix = models.CharField(max_length=20, null=True, blank=True)
    start_date = models.DateField(default=datetime.utcnow)
    state = models.BooleanField(default=True)
    leave = models.BooleanField(default=False)
    type = models.CharField(max_length=64,null=True,blank=True)
    _username = models.CharField(max_length=64)
    primary_job = models.ForeignKey(JobRole, related_name='primary_job', null=True, blank=True, on_delete=models.SET_NULL)
    jobs = models.ManyToManyField(JobRole, blank=True)
    photo = models.FileField(upload_to='uploads/', null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    _password = models.CharField(max_length=128,null=True,blank=True)
    _email_alias = models.CharField(max_length=128, null=True, blank=True, unique=True)

    def __eq__(self,other) -> bool:
        if not isinstance(other,Employee) or self.emp_id != other.pk:
            return False

        for field in ['givenname','middlename','surname','suffix','start_date','state','leave',
                      'type','username','photo','email_alias']:
            if getattr(self,field) != getattr(other,field):
                return False
        
        if (self.manager is None and other.manager is not None or
            self.manager is not None and other.manager is None):
            return False
        elif self.manager and other.manager and self.manager.pk != other.manager.pk:
            return False
        if (self.location is None and other.location is not None or
            self.location is not None and other.location is None):
            return False
        elif self.location and other.location and self.location.pk != other.location.pk:
            return False
        if (self.primary_job is None and other.primary_job is not None or
            self.primary_job is not None and other.primary_job is None):
            return False
        elif self.primary_job and other.primary_job and self.primary_job.pk != other.primary_job.pk:
            return False

        return True

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def clear_password(self,confirm=False):
        if confirm:
            self._password = None
            self.save()

    @property
    def password(self) -> str:
        if self._password:
            return FieldEncryption().decrypt(self._password)
        return None

    @password.setter
    def password(self, passwd: str) -> None:
        self._password = FieldEncryption().encrypt(passwd)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self,username:str) -> None:
        set_username(self, username)

    @property
    def email_alias(self):
        return self._email_alias or self.username

    @email_alias.setter
    def email_alias(self,val):
        set_upn(self,val)

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
        elif isinstance(new_status,str) and new_status.lower() in [self.STAT_ACT,self.STAT_LEA,self.STAT_TERM]:
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

    @property
    def secondary_jobs(self):
        return self.jobs

    @secondary_jobs.setter
    def secondary_jobs(self,jobs):
        """
        Set the jobs field based on the provided value. The value can be
        a list,tuple,dict*,int or string. for strings we will try and 
        split the string either by whitespace or comma.
        
        * For dicts we'll only use the values. 

        Args:
            jobs (Any): the job ID or list of job IDs

        Raises:
            ValueError: If we cannont conver the provided job(s) to a list
            ValueError: If the Job ID is not a valid int
        """
        if isinstance(jobs,str):
            jobs = jobs.split()
            if len(jobs) == 1:
                jobs = jobs[0].split(',')

        elif isinstance(jobs,dict):
            jobs = jobs.values()

        elif isinstance(jobs,int):
            jobs = [str(jobs)]

        elif isinstance(jobs,tuple):
            jobs = list(jobs)

        if not isinstance(jobs,list):
            raise ValueError(f"Unable to convert {type(jobs)} to list")  

        jl = []
        for job in jobs:
            try:
                jl.append(JobRole.objects.get(pk=int(job)))
            except JobRole.DoesNotExist:
                logger.warning(f"Job ID {job} doesn't exists yet")

        try:
            self.jobs.add(*jl)
        except ValueError:
            logger.info("Can't set the jobs until the model has been saved")

    @property
    def firstname(self) -> str:
        return self.givenname

    @property
    def lastname(self) -> str:
        return self.surname

    def __str__(self):
        return f"{self.emp_id}: {self.givenname} {self.surname}"

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        if created:
            passwd = "".join(choice(ascii_letters + digits) for char in range(9))
            passwd = choice(ascii_lowercase) + passwd + choice(digits) + choice(ascii_uppercase)

            instance.password = passwd
            instance.save()

            #instanciate the EmployeeOverride Table
            override = EmployeeOverrides()
            override.employee = instance
            override.save()

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        try:
            if instance.emp_id:
                prev_instance = Employee.objects.get(pk=instance.emp_id)
            else:
                prev_instance = None
        except Employee.DoesNotExist:
            prev_instance = None

        if prev_instance:
            if (prev_instance.status == instance.STAT_TERM and
                    instance.status != instance.STAT_TERM):
                logger.info(f"{instance} transitioned from terminated to active")
                set_username(instance)
                set_upn(instance)
            elif (prev_instance.status != instance.STAT_TERM and
                    instance.status == instance.STAT_TERM):
                logger.info(f"{instance} transitioned from active to terminated")
                set_username(instance, f"{instance._username}{round(time.time())}")
                set_upn(instance, f"{instance._username}{round(time.time())}")

            if prev_instance != instance:
                instance.updated_on = datetime.utcnow()

        if instance._username is None:
            set_username(instance)

        if instance._email_alias is None:
            set_upn(instance)


# Employee Model signal connections
pre_save.connect(Employee.pre_save, sender=Employee)
post_save.connect(Employee.post_save, sender=Employee)


class EmployeeOverrides(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, unique=True)
    _firstname = models.CharField(max_length=96, null=True, blank=True)
    _lastname = models.CharField(max_length=96, null=True, blank=True)
    nickname = models.CharField(max_length=96, null=True, blank=True)
    _location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    designations = models.CharField(max_length=128, null=True, blank=True,)

    def __str__(self) -> str:
        return f"{self.employee.emp_id}: {self.firstname} {self.lastname}"

    def __eq__(self, other) -> bool:
        if not isinstance(other,EmployeeOverrides):
            return False

        for field in ['employee','_firstname','_lastname','nickname','_location']:
            if getattr(self,field) != getattr(other,field):
                return False

        return True

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    @property
    def username(self):
        """
        Returns the Employees Username Exists for conitinuity
        """
        return self.employee.username

    @username.setter
    def username(self,username:str) -> None:        
        set_username(self.employee, username)

    @property
    def firstname(self):
        return self._firstname or self.employee.givenname

    @firstname.setter
    def firstname(self,val):
        self._firstname = val

    @property
    def lastname(self):
        return self._lastname or self.employee.surname

    @lastname.setter
    def lastname(self,val):
        self._lastname = val

    @property
    def location(self):
        return self._location or self.employee.location

    @location.setter
    def location(self,val):
        self._location = val

    @property
    def email_alias(self):
        return self.employee.email_alias

    @email_alias.setter
    def email_alias(self,val):
        self.employee.email_alias = val

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        try:
            prev_instance = EmployeeOverrides.objects.get(employee=instance.employee)
        except EmployeeOverrides.DoesNotExist:
            prev_instance = None

        if prev_instance and prev_instance != instance:
            if instance._firstname or instance._lastname:
                set_username(instance)
                set_upn(instance)
            instance.employee.updated_on = datetime.utcnow()


#Employee Override Model Signal Connects
pre_save.connect(EmployeeOverrides.pre_save, sender=EmployeeOverrides)


class EmployeePhone(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    label = models.CharField(max_length=50, default="Primary")
    number = models.CharField(max_length=20)
    primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{str(self.employee)} - {self.label} {self.number}"


class EmployeeAddress(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    label = models.CharField(max_length=50, default="Primary")
    street1 = models.CharField(max_length=128)
    street2 = models.CharField(max_length=128)
    street3 = models.CharField(max_length=128)
    province = models.CharField(max_length=128)
    city = models.CharField(max_length=128)
    postal_code = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{str(self.employee)} - {self.label}"


class EmployeePending(models.Model):
    class Meta:
        db_table = 'employeepending'

    STAT_TERM = Employee.STAT_TERM
    STAT_ACT = Employee.STAT_ACT
    STAT_LEA = Employee.STAT_LEA

    created_on = models.DateField(null=False, blank=False, default=datetime.utcnow)
    updated_on = models.DateField(null=False, blank=False, default=datetime.utcnow)
    manager = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
    firstname = models.CharField(max_length=96, null=False, blank=False)
    lastname = models.CharField(max_length=96, null=False, blank=False)
    suffix = models.CharField(max_length=20, null=True, blank=True)
    designation = models.CharField(max_length=128, null=True, blank=True)
    start_date = models.DateField(default=datetime.utcnow)
    state = models.BooleanField(default=True)
    leave = models.BooleanField(default=False)
    type = models.CharField(max_length=64,null=True,blank=True)
    _username = models.CharField(max_length=64)
    primary_job = models.ForeignKey(JobRole, related_name='pending_primary_job', null=True,
                                    blank=True, on_delete=models.SET_NULL)
    jobs = models.ManyToManyField(JobRole, blank=True)
    photo = models.FileField(upload_to='uploads/', null=True, blank=True)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    _password = models.CharField(max_length=128,null=True,blank=True)
    _email_alias = models.CharField(max_length=128, null=True, blank=True, unique=True)
    employee = models.ForeignKey(Employee, related_name='pending_employee', null=True, blank=True, on_delete=models.CASCADE)
    guid = models.CharField(max_length=40,null=True,blank=True)
    
    def __eq__(self,other) -> bool:
        if not isinstance(other,EmployeePending) or self.pk != other.pk:
            return False

        for field in ['firstname','lastname','suffix','start_date','state','leave',
                      'type','username','photo','email_alias','guid']:
            if getattr(self,field) != getattr(other,field):
                return False
        
        if (self.manager is None and other.manager is not None or
            self.manager is not None and other.manager is None):
            return False
        elif self.manager and other.manager and self.manager.pk != other.manager.pk:
            return False
        if (self.location is None and other.location is not None or
            self.location is not None and other.location is None):
            return False
        elif self.location and other.location and self.location.pk != other.location.pk:
            return False
        if (self.primary_job is None and other.primary_job is not None or
            self.primary_job is not None and other.primary_job is None):
            return False
        elif self.primary_job and other.primary_job and self.primary_job.pk != other.primary_job.pk:
            return False

        return True

    def __str__(self) -> str:
        return f"{self.firstname} {self.lastname}"

    def clear_password(self,confirm=False):
        if confirm:
            self._password = None
            self.save()

    @property
    def password(self) -> str:
        if self._password:
            return FieldEncryption().decrypt(self._password)
        return None

    @password.setter
    def password(self, passwd: str) -> None:
        self._password = FieldEncryption().encrypt(passwd)

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self,username:str) -> None:
        set_username(self, username)

    @property
    def email_alias(self):
        if not self._email_alias:
            return self.username
        return self._email_alias

    @email_alias.setter
    def email_alias(self,val):
        set_upn(val)

    @property
    def emp_id(self) -> int:
        #When called return 0 as this employee has not been commited/assigned an employee id yet.
        return 0

    @property
    def givenname(self) -> str:
        return self.firstname

    @property
    def surname(self) -> str:
        return self.lastname

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
        elif isinstance(new_status,str) and new_status.lower() in [self.STAT_ACT,self.STAT_LEA,self.STAT_TERM]:
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

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        if created:
            passwd = "".join(choice(ascii_letters + digits) for char in range(9))
            passwd = choice(ascii_lowercase) + passwd + choice(digits) + choice(ascii_uppercase)

            instance.password = passwd
            instance.save()

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        try:
            if instance.pk:
                prev_instance = EmployeePending.objects.get(pk=instance.pk)
            else:
                prev_instance = None
        except EmployeePending.DoesNotExist:
            prev_instance = None

        if prev_instance:
            if (prev_instance.status == instance.STAT_TERM and
                    instance.status != instance.STAT_TERM):
                logger.info(f"{instance} transitioned from terminated to active")
                set_username(instance)
                set_upn(instance)
            elif (prev_instance.status != instance.STAT_TERM and
                    instance.status == instance.STAT_TERM):
                logger.info(f"{instance} transitioned from active to terminated")
                set_username(instance, f"{instance._username}{round(time.time())}")
                set_upn(instance, f"{instance._username}{round(time.time())}")

            if prev_instance != instance:
                instance.updated_on = datetime.utcnow()

        if instance._username is None:
            set_username(instance)

        if instance._email_alias is None:
            set_upn(instance)


#Employee Pending signal connect
pre_save.connect(EmployeePending.pre_save, sender=EmployeePending)
post_save.connect(EmployeePending.post_save, sender=EmployeePending)


class GroupMapping(models.Model):
    dn = models.CharField(max_length=256)
    jobs = models.ManyToManyField(JobRole, blank=True)
    bu = models.ManyToManyField(BusinessUnit, blank=True)
    loc = models.ManyToManyField(Location, blank=True)


class WordList(models.Model):
    src = models.CharField(max_length=256)
    replace = models.CharField(max_length=256)

    def __str__(self):
        return f"{self.src} -> {self.replace}"


class CsvPending(models.Model):
    class Meta:
        db_table = 'csv_pending'

    emp_id = models.IntegerField(primary_key=True)
    givenname = models.CharField(max_length=96,blank=True)
    surname = models.CharField(max_length=96,blank=True)
    row_data = models.TextField()
    
    @property
    def firstname(self):
        return self.givenname

    @firstname.setter
    def firstname(self,val):
        self.givenname = val

    @property
    def lastname(self):
        return self.surname

    @lastname.setter
    def lastname(self,val):
        self.surname = val

    def __str__(self):
        return f"{self.emp_id} - {self.givenname} {self.surname}"