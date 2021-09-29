import logging
import time

from hirs_admin.models import Setting
from pathlib import Path

logger = logging.getLogger('test.setup_tests')

def set_configuration(group:str,config:dict) -> None:
    PATH = group + Setting.FIELD_SEP + '%s' + Setting.FIELD_SEP + '%s'

    for key,val in config.items():
        if type(val) == dict:
            for item,data in val.items():
                try:
                    obj = Setting.o2.get(setting=PATH % (key,item))
                    obj.value = data
                    obj.save()
                except Setting.DoesNotExist:
                    logger.exception("WHAT THE FUCK: " + PATH % (key,item))
                    raise Exception("Wham!")
                    
def setup_hirs_admin():
    from hirs_admin.models import WordList

    wl = {
        'mgr': 'Manager',
        'Dir': 'Director'
    }

    for key,val in wl.items():
        w,_ = WordList.objects.get_or_create(src=key)
        w.replace = val
        w.save()

def setup_hirs_admin_after():
    from hirs_admin.models import JobRole,BusinessUnit,Location,GroupMapping
    
    job = GroupMapping()
    job.dn = "CN=test group,OU=groups,OU=testing,DC=wch,DC=net"
    job.save()
    
    loc = GroupMapping()
    loc.dn = "CN=test location,OU=groups,OU=testing,DC=wch,DC=net"
    loc.save()
    
    bu = GroupMapping()
    bu.dn = "CN=test bu,OU=groups,OU=testing,DC=wch,DC=net"
    bu.save()

    for obj in JobRole.objects.all():
        job.jobs.add(obj)

    for obj in BusinessUnit.objects.all():
        bu.bu.add(obj)

    for obj in Location.objects.all():
        loc.loc.add(obj)

    job.save()
    loc.save()
    bu.save()

def setup_ftp_import():
    from ftp_import.helpers import config

    module_config = {
        config.CAT_SERVER: {
            config.SERVER_SERVER: None,
            config.SERVER_PROTOCAL: 'sftp',
            config.SERVER_PORT: '22',
            config.SERVER_USER: None,
            config.SERVER_PASSWORD: None,
            config.SERVER_SSH_KEY: None,
            config.SERVER_PATH: '.',
            config.SERVER_FILE_EXP: '.*'
        },
        config.CAT_CSV: {
            config.CSV_FIELD_SEP: ',',
            config.CSV_FAIL_NOTIF: '',
            config.CSV_IMPORT_CLASS: 'ftp_import.forms',
            config.CSV_USE_EXP: 'True'
        },
        config.CAT_FIELD: {
            config.FIELD_LOC_NAME: 'll4_desc',
            config.FIELD_JD_NAME: 'll7_desc',
            config.FIELD_JD_BU: 'll5',
            config.FIELD_BU_NAME: 'll5_desc',
            config.FIELD_BU_PARENT: None,
            config.FIELD_STATUS: 'employee_status',
        },
        config.CAT_EXPORT: {
            config.EXPORT_ACTIVE: 'AC',
            config.EXPORT_TERM: 'TER',
            config.EXPORT_LEAVE: 'L',
        },
    }

    set_configuration(config.GROUP_CONFIG,module_config)

    fields = config.get_fields()
    field_conf = {
        'employee_number': 'emp_id',
        'first_name': 'givenname',
        'last_name': 'surname',
        'employee_status': 'status',
        'address': 'street1',
        'city': 'city',
        'province': 'province',
        'zip': 'postal_code',
        'country': 'country',
        'phone_1': 'number',
        'll7': 'primary_job',
        'll4': 'location',
        'reports_to': 'manager',
        'secondarylabour': 'secondary_jobs',
    }

    for key,value in field_conf.items():
        if key in fields.keys():
            s = Setting.o2.get_by_path(config.GROUP_MAP,key,'map_to')
            try:
                s = s[0]
                s.value = value
                s.save()
                s = Setting.o2.get_by_path(config.GROUP_MAP,key,'import')
                s = s[0]
                s.value = 'True'
                s.save()

            except IndexError:
                logger.warning(f"field {key} doesn't exists")

def setup_ad_export():
    from ad_export.helpers import config

    print("Please set your upn domain and route address")
    module_config = {
        config.CONFIG_CAT: {
            config.CONFIG_NEW_NOTIFICATION:'',
            config.CONFIG_AD_USER: 'importadmin',
            config.CONFIF_AD_PASSWORD: 'quiuj5Aegh$ief3iXee1d',
            config.CONFIG_UPN: 'wch.net',
            config.CONFIG_ROUTE_ADDRESS: 'thecarswells-ca.mail.onmicrosoft.com',
            config.CONFIG_ENABLE_MAILBOXES: 'True',
            config.CONFIG_MAILBOX_TYPE: 'remote',
            config.CONFIG_LAST_SYNC:'1999-01-01 00:00'
        },
        config.EMPLOYEE_CAT: {
            config.EMPLOYEE_DISABLE_LEAVE: 'False',
            config.EMPLOYEE_LEAVE_GROUP_ADD: 'active user',
            config.EMPLOYEE_LEAVE_GROUP_DEL: 'leave user',
        },
        config.DEFAULTS_CAT: {
            config.DEFAULT_ORG: 'Constco',
            config.DEFAULT_PHONE: '',
            config.DEFAULT_FAX: '',
            config.DEFAULT_STREET: '123 Harlem Ave',
            config.DEFAULT_PO: '',
            config.DEFAULT_CITY: 'Regina',
            config.DEFAULT_STATE: 'Saskatchewam',
            config.DEFAULT_ZIP: 'S4S 4S4',
            config.DEFAULT_COUNTRY: 'CA'
        }
    }

    set_configuration(config.GROUP_CONFIG,module_config)

def setup_smtp():
    from smtp_client.helpers import config
    
    print("Please set your defaults for testing")
    module_config = {
        config.CAT_CONFIG: {
            config.SERVER_SERVER: 'localhost',
            config.SERVER_PORT: '25',
            config.SERVER_TLS: 'False',
            config.SERVER_SSL: 'False',
            config.SERVER_USERNAME: '',
            config.SERVER_PASSWORD: ['',True],
            config.SERVER_SENDER: '',
        },
    }

    set_configuration(config.GROUP_CONFIG,module_config)

def import_employees():
    from ftp_import.csv import CsvImport
    from ftp_import.helpers.stats import Stats
    Stats.time_start = time.time()

    path = str(Path(__file__).resolve().parent) + '\\employee_data.csv'
    with open(path) as csv:
        CsvImport(csv)

    Stats.time_end = time.time()
    logger.info(f"Import Stat:\n{Stats()}")

def run_ad_export():
    import ad_export
    ad_export.run()

def run_setup():
    import setup
    setup.setup(service=False)
    setup_hirs_admin()
    setup_ftp_import()
    setup_ad_export()
    import_employees()
    setup_hirs_admin_after()

def send_email():
    from smtp_client import smtp
    dest = input(f"Send Test Email to: ")
    s = smtp.Smtp()
    s.send(dest,"Test email sent from setup_tests.send_email()","HRIS Sync Test Email")

if __name__ == "__main__":
    import os
    if not hasattr(os.environ,'DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hirs_integration.settings')
        import django
        django.setup()

    run_setup()
    run_ad_export()
    