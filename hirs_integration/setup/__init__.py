import hirs_admin
import cron
import ftp_import
import ad_export
import corepoint_export
import smtp_client
import subprocess
import sys
import os
import string

from random import choice
from django.conf import settings
from time import sleep

def setup(service=True):
    if service:
        nssm = str(settings.BASE_DIR) + "\\bin\\nssm.exe"
        srv_name = 'hris_integration_cron'
        if not os.path.exists(nssm):
            print(f"Sorry the nssm executable doesn't seem to exist at {nssm}")
            sys.exit(-1)

    from django.contrib.auth.models import User
    qs = User.objects.filter(email='admin@example.com')
    if len(qs) == 0:
        pw = "".join(choice(string.ascii_letters + string.digits + string.punctuation) for char in range(15))
        User.objects.create_superuser('admin@example.com', 'admin', pw)
        print(f"Admin user 'admin' created with password '{pw}'")

    hirs_admin.setup()
    cron.setup()
    ftp_import.setup()
    ad_export.setup()
    corepoint_export.setup()
    smtp_client.setup()

    from ftp_import.csv import CsvImport
    with open(str(settings.BASE_DIR) + '\\ftp_csv_headers.csv', 'r') as f:
        CsvImport(f)

    if service:
        subprocess.run([nssm,'install',srv_name,sys.executable])
        subprocess.run([nssm,'set',srv_name,'AppParameters','%s\\cron\\service.py'])
        subprocess.run([nssm,'set',srv_name,'AppDirectory',str(settings.BASE_DIR)])
        subprocess.run([nssm,'set',srv_name,'AppStdout',str(settings.LOG_DIR) + "\\cron_service.out"])

def create_keys():
    from django.core.management import utils
    from cryptography.fernet import Fernet
    print("Paste the following two lines into you settings.py:\n")
    print(f"SECRET_KEY = '{utils.get_random_secret_key()}'")
    print(f"ENCRYPTION_KEY = '{Fernet.generate_key().decode('utf-8')}'")