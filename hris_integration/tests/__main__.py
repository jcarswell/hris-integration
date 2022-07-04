import os
import sys
import django

if sys.version_info.major < 3 and sys.version_info.minor < 8:
    print("Python 3.8 or higher is required to run this application.")
    sys.exit(1)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hris_integration.settings")

django.setup()

import tests.setup_tests

tests.setup_tests.run_setup()
g = input("Run AD Export? [y/N]: ").lower()
if g == "y":
    tests.setup_tests.run_ad_export()
g = input("Send Test Email? [y/N]: ").lower()
if g == "y":
    tests.setup_tests.send_email()
    tests.setup_tests.send_email_html()
