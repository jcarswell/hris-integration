import os

from django.conf import settings

from .apps import CronConfig
from .exceptions import AlreadyExists,ModuleOrMethodInvalid

__all__ = ("Setup","install_service","CronConfig",'AlreadyExists','ModuleOrMethodInvalid')

def setup():
    """No setup tasks required at this time"""
    pass

def install_service():
    import subprocess
    import sys

    nssm = str(settings.BASE_DIR) + "\\bin\\nssm.exe"
    srv_name = 'hirs_integration_cron'
    if not os.path.exists(nssm):
        print(f"Sorry the nssm executable doesn't seem to exist at {nssm}")
        sys.exit(-1)

    subprocess.run([nssm,'install',srv_name,sys.executable])
    subprocess.run([nssm,'set',srv_name,'AppParameters','%s\\cron\\service.py'])
    subprocess.run([nssm,'set',srv_name,'AppDirectory',str(settings.BASE_DIR)])
    subprocess.run([nssm,'set',srv_name,'AppStdout',str(settings.LOG_DIR) + "\\cron_service.out"])