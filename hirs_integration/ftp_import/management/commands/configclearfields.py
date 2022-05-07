# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Clears the FTP Import fields from the database"
    requires_migrations_checks = True
    requires_system_checks = []
    
    def handle(self, *args, **kwargs):
        from settings.models import Setting
        from ftp_import.helpers import settings 
        self.stdout.write(self.style.NOTICE("Clearing all ftp import fields"))
        for f in Setting.o2.get_by_path(settings.MAP_GROUP):
            self.stdout.write(self.style.NOTICE(f"[VERBOSE] Deleting {f.setting}"))
            f.delete()