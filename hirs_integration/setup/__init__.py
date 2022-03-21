# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

import hirs_admin
import cron
import ftp_import
import ad_export
import corepoint_export
import smtp_client
import string

from random import choice
from django.conf import settings

def setup(service=False):

    from django.contrib.auth.models import User
    qs = User.objects.filter(email='admin@example.com')
    if len(qs) == 0:
        pw = "".join(choice(string.ascii_letters + string.digits) for char in range(24))
        User.objects.create_superuser('admin', email='admin@example.com', password=pw)

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
        cron.install_service()

    if len(qs) == 0:
        print(f"Admin user 'admin' created with password '{pw}'")


def create_keys():
    from django.core.management import utils
    from cryptography.fernet import Fernet
    print("Paste the following two lines into you settings.py:\n")
    print(f"SECRET_KEY = '{utils.get_random_secret_key()}'")
    print(f"ENCRYPTION_KEY = '{Fernet.generate_key().decode('utf-8')}'")