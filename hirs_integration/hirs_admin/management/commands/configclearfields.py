from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Clears the FTP Import fields from the database"
    requires_migrations_checks = True
    requires_system_checks = []
    
    def handle(self, *args, **kwargs):
        from hirs_admin.models import Setting
        from ftp_import.helpers import settings 
        print("Clearing all ftp import fields")
        for f in Setting.o2.get_by_path(settings.MAP_GROUP):
            print(f"[VERBOS] Deleting {f.setting}")
            f.delete()