import string
import logging

from django.db import models
from datetime import datetime
from cryptography.fernet import Fernet
from django import conf
from django.db.models.query import QuerySet
from django.db.models.signals import pre_save,post_save
from random import choice
from django.utils.translation import gettext_lazy as _t
from string import ascii_letters, digits, capwords

logger = logging.getLogger('AdminSite.Model')

# Helper Functions
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
    invalid_char = ['!','@','#','$','%','^','&','*','(',')','_','+','=',';',':','\'','"',',','<','>','.',' ','`','~']
    substitue = ''
    suffix = suffix or ""
    allowed_char = allowed_char or []
        
    u = first[0] + (last or first[1:])
    
    for x in range(len(u)):
        if u[x] in invalid_char and not u[x] in allowed_char:
            u[x] = substitue
            
    return u + suffix

def set_username(instance, username:str =None) -> None:
    """Validate and set the username paramater

    Args:
        username (str, optional): username for the user if blank we'll use the database feilds
    """
    
    if username:
        username = username_validator(username)
    
    elif isinstance(instance,EmployeeOverrides):
        # If we are using the EmployeeOverrides table it is possible that the
        # Firstname or Lastname feild is not set. We will need to use the correct
        # information from the Employee Table
        employee = Employee.objects.get(instance.employee)
        username = username_validator(
            (instance.firstname or employee.givenname),
            (instance.lastname or employee.surname)
        )
    
    else:
        username = username_validator(instance.givenname, instance.surename)
    
    if instance.username == username:
        return
    
    while instance.username != username:
        suffix = ''
        username = username_validator(username, suffix=suffix)
        if (Employee.objects.filter(_username=username).exists()
                or EmployeeOverrides.objects.filter(_username=username).exists()):
            if suffix == '':
                suffix = 1
            else:
                suffix = suffix + 1
        else:
            instance._username = username

class FeildEncryption:
    def __init__(self) -> None:
        try:
            self.key = Fernet(conf.settings.ENCRYPTION_KEY)
        except Exception:
            raise ValueError("Encryption key is not available, check SECRET_KEY and SALT")
    
    def enrypt(self,data:str) -> str:
        try:
            return self.key.encrypt(data)
        except Exception as e:
            logger.critical("An Error occured encypting the data provided")
            raise ValueError from e
    
    def decrypt(self,data:str) -> str:
        try:
            self.key.decrypt(data)
        except Exception as e:
            logger.critical("An Error occured decypting the data provided")
            raise ValueError from e

# Models

class SettingsManager(models.Manager):
    def get_by_path(self, group:str, catagory:str =None, item:str =None) -> QuerySet:
        path = catagory
        if group:
            path = path + Setting.FIELD_SEP + group
        else:
            path = path + Setting.FIELD_SEP
            return self.filter(setting__startswith=path)
        
        if item:
            path = path + Setting.FIELD_SEP +  item
            return self.filter(setting=path).value
        else:
            path = path + Setting.FIELD_SEP
            return self.filter(setting__startswith=path)

class Setting(models.Model):
    """Application Settings"""
    FIELD_SEP = '/'
    class Meta:
        db_table = 'setting'
    setting = models.CharField(max_length=128,unique=True)
    _value = models.TextField()
    hidden = models.BooleanField(default=False)
    
    objects = SettingsManager

    @property
    def value(self) -> str:
        if self.hidden:
            return FeildEncryption().decrypt(self._value)
        else:
            return self._value
      
    @value.setter  
    def value(self, value:str) -> None:
        self._value = FeildEncryption().enrypt(value)

    def __str__(self):
        return f"{self.setting} - {self._value}"

    @classmethod
    

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        """Ensure the the value is encrypted if the feild is set as hidden"""
        for char in instance.setting:
            if char not in ascii_letters + digits + cls.FIELD_SEP + '_-':
                instance.setting.replace(char,'_')
        if len(instance.setting.split(cls.FIELD_SEP)) != 3:
            raise ValueError("setting does not contain proper format, should be group/catagory/item")

        if instance.hidden:
            try:
                _ = instance.decrypt_value()
            except Exception:
                instance.encrypt_value(instance.value)    
    
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
    emp_id = models.IntegerField(primary_key=True)
    created_on = models.DateField(null=False, blank=False, default=datetime.utcnow)
    updated_on = models.DateField(null=False, blank=False, default=datetime.utcnow)
    manager = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL)
    givenname = models.CharField(max_length=96, null=False, blank=False)
    middlename = models.CharField(max_length=96)
    surname = models.CharField(max_length=96, null=False, blank=False)
    suffix = models.CharField(max_length=20)
    start_date = models.DateField(default=datetime.utcnow)
    end_date = models.DateField()
    state = models.BooleanField(default=True)
    leave = models.BooleanField(default=True)
    _username = models.CharField(max_length=64)
    primary_job = models.ForeignKey(JobRole, related_name='primary_job', null=True, blank=True, on_delete=models.SET_NULL)
    jobs = models.ManyToManyField(JobRole, blank=True)
    photo = models.FileField(upload_to='uploads/')
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    _password = models.CharField(max_length=128,null=True,blank=True)

    @property
    def username(self):
        """
        Returns the username for the user either from current set value or
        if set the overridden username.

        Returns:
            str: The Overridden Employees Useraname
        """
        
        employee = EmployeeOverrides.objects.get(employee=self.pk)
        if len(employee) == 1:
            return employee.username or self._username
        
        return self._username
    
    @property
    def password(self) -> str:
        return FeildEncryption().decrypt(self._password)
    
    @password.setter
    def password(self, passwd: str) -> None:
        self._password = FeildEncryption().enrypt(passwd)

    @username.setter
    def username(self,username:str) -> None:
        set_username(self, username)

    def update_username(self):
        set_username(self)
    
    @property
    def status(self):
        if self.state and self.leave:
            return "Leave"
        elif self.state:
            return "Active"
        else:
            return "Terminated"
        
    def __str__(self):
        return f"{self.givenname} {self.surname}"

    @classmethod
    def post_save(cls, sender, instance, created, **kwargs):
        if created:
            passwd = "".join(choice(string.ascii_letters + string.digits) for char in range(12))
            instance.password(passwd)
            instance.save()

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        if instance.username is None:
            instance.set_username(instance)
        
        if update_fields:
            instance.updated_on = datetime.utcnow()
pre_save.connect(Employee.pre_save, sender=Employee)
post_save.connect(Employee.post_save, sender=Employee)


class EmployeeOverrides(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, unique=True)
    firstname = models.CharField(max_length=96)
    lastname = models.CharField(max_length=96)
    nickname = models.CharField(max_length=96)
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    _username = models.CharField(max_length=128)
    email_alias = models.CharField(max_length=128)
    
    @property
    def username(self):
        """
        Returns the username for the user either from current set value or
        if set the overridden username.

        Returns:
            str: The Employees Useraname
        """
        if not self._username:
            employee = Employee.objects.get(self.employee)
            return employee.username
        return self._username
    
    @username.setter
    def username(self,username:str) -> None:
        set_username(self, username)

    def update_username(self):
        set_username(self)

    @classmethod
    def pre_save(cls, sender, instance, raw, using, update_fields, **kwargs):
        if instance.username is None and instance.firstname is not None or instance.lastname is not None:
            instance.set_username(instance)
        
        emp = Employee.objects.get(instance.employee)
        emp.updated_on = datetime.utcnow()
        emp.save()
pre_save.connect(EmployeeOverrides.pre_save, sender=EmployeeOverrides)


class EmployeeDesignation(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    label = models.CharField(max_length=50)


class EmployeePhone(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    label = models.CharField(max_length=50, default="Primary")
    number = models.IntegerField()
    countrycode = models.IntegerField(default=1)
    primary = models.BooleanField()

    def __str__(self):
        return self.number


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
    primary = models.BooleanField()


class EmployeePending(models.Model):
    class Meta:
        db_table = 'employeepending'
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)


class GroupMapping(models.Model):
    dn = models.CharField(max_length=256)
    jobs = models.ManyToManyField(JobRole)
    bu = models.ManyToManyField(BusinessUnit)
    loc = models.ManyToManyField(Location)


class WordList(models.Model):
    src = models.CharField(max_length=256)
    replace = models.CharField(max_length=256)
    
    def __str__(self):
        return f"{self.src} -> {self.replace}"

class BusinessUnitManager(models.Model):
    bu = models.OneToOneField(BusinessUnit, on_delete=models.CASCADE, unique=True)
    manager = models.ForeignKey(Employee, null=True, blank=True, on_delete=models.SET_NULL)
