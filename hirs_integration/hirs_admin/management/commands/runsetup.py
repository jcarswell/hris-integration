from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Import the base configuration and install the cron service"
    requires_migrations_checks = True
    requires_system_checks = []
    
    def add_arguments(self,parser):
        parser.add_argument('--no-service',action='store_true',help="don't try to install/update the cron job service")
    
    def handle(self, *args, **kwargs):
        import setup
        setup.setup(not kwargs['no_service'])