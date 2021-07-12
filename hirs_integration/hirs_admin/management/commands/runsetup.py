from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Import the base configuration and install the cron service"
    requires_migrations_checks = True
    requires_system_checks = []
    
    def handle(self, *args, **kwargs):
        import setup
        setup.setup()