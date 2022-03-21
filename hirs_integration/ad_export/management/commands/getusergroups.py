# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Run the AD Export job"
    requires_migrations_checks = True
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            nargs='+',
            type=int,
            help='get groups for specified employee IDs'
        )
        parser.add_argument(
            '--username',
            nargs='+',
            type=str,
            help='get groups for specified usernames'
        )
        parser.add_argument(
            '--emailalias',
            nargs='+',
            type=str,
            help='get groups for specified email aliases'
        )

    def handle(self, *args, **kwargs):
        emps = self.get_emps(kwargs['id'],kwargs['username'],kwargs['emailalias'])
        for e in emps:
            self.stdout.write(self.style.SUCCESS(str(e)))
            self.stdout.write(self.style.NOTICE('Adding Groups'))
            self.stdout.writelines(e.groups_add())
            self.stdout.write(self.style.WARNING('Removing Groups'))
            self.stdout.writelines(e.groups_remove())

    def get_emps(self,ids=None,users=None,aliases=None):
        from ad_export.helpers import config
        from hirs_admin.models import Employee,EmployeePending
        emps = []

        if ids:
            for id in ids:
                try:
                    emps.append(
                        config.EmployeeManager(Employee.objects.get(pk=id))
                    )
                except Employee.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"No employee with id {id}"))

        if users:
            for user in users:
                emp = None
                try:
                    emp = Employee.objects.get(_username=user)
                except Employee.DoesNotExist:
                    try:
                        emp = EmployeePending.objects.get(_username=user)
                    except EmployeePending.DoesNotExist:
                        self.stderr.write(self.style.ERROR(f"No username found: {user}"))

                if isinstance(emp,(EmployeePending,Employee)):
                    emps.append(config.EmployeeManager(emp))
                else:
                    for e in emp:
                        emps.append(config.EmployeeManager(e))

        if aliases:
            for alias in aliases:
                emp = None
                try:
                    emp = Employee.objects.get(_email_alias=alias)
                except Employee.DoesNotExist:
                    try:
                        emp = EmployeePending.objects.get(_email_alias=alias)
                    except EmployeePending.DoesNotExist:
                        self.stderr.write(self.style.ERROR(f"No username found: {alias}"))

                if isinstance(emp,(EmployeePending,Employee)):
                    emps.append(config.EmployeeManager(emp))
                else:
                    for e in emp:
                        emps.append(config.EmployeeManager(e))

        return emps