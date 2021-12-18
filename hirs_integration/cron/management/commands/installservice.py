from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Install the cron server"
    requires_migrations_checks = True
    requires_system_checks = []
    
    def handle(self, *args, **kwargs):
        from cron import install_service
        install_service()
        