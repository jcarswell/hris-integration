# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Install the cron server"
    requires_migrations_checks = True
    requires_system_checks = []
    
    def handle(self, *args, **kwargs):
        from cron import install_service
        install_service()
        