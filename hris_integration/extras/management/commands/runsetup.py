# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import the base configuration and install the cron service"
    requires_migrations_checks = True
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--service", action="store_true", help="Install the cron job service"
        )
        parser.add_argument(
            "--username", type=str, help="Admin account username. Defaults to 'admin'"
        )
        parser.add_argument(
            "--email",
            type=str,
            help="Admin account email. Defaults to 'admin@example.com'",
        )
        parser.add_argument(
            "--password",
            type=str,
            help="Admin account password. Defaults to randomly generated password",
        )

    def handle(self, *args, **kwargs):
        from setup import django

        setup_args = {
            k: v
            for k, v in kwargs.items()
            if v is not None and k in ["service", "username", "email", "password"]
        }
        django.setup(**setup_args)
