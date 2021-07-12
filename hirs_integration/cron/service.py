import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os

from pathlib import Path

sys.path.append(Path(__file__).resolve.parent.parrent)
os.environ['DJANGO_SETTINGS_MODULE'] = 'hirs_integration.settings'

from django.conf import settings

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "hirs_integration_cron"
    _svc_display_name_ = "HIRS Integration Cron runner"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        del(self.proc)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.main()

    def main(self):
        from .cron import Runner
        self.proc = Runner()

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(AppServerSvc)