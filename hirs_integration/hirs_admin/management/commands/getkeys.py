from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Get new sercret and encyption keys"
    requires_migrations_checks = False
    requires_system_checks = []
    
    def handle(self, *args, **kwargs):
        import setup
        setup.create_keys()