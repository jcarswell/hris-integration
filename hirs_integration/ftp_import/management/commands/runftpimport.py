from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Run the FTP Import job"
    requires_migrations_checks = True
    requires_system_checks = []


    def handle(self, *args, **kwargs):
        import ftp_import
        ftp_import.run()