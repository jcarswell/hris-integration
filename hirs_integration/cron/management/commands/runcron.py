from django.core.management.base import BaseCommand,CommandError
from hirs_integration.cron import Runner

class Command(BaseCommand):
    help = "Start the cron server"
    requires_migrations_checks = True
    requires_system_checks = []
    
    def handle(self, *args, **kwargs):
        Runner()