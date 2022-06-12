# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Run the AD Export job"
    requires_migrations_checks = True
    requires_system_checks = []

    def add_arguments(self, parser):
        parser.add_argument(
            "--id", nargs="+", type=int, help="get groups for specified employee IDs"
        )
        parser.add_argument(
            "--username", nargs="+", type=str, help="get groups for specified usernames"
        )
        parser.add_argument(
            "--emailalias",
            nargs="+",
            type=str,
            help="get groups for specified email aliases",
        )

    def handle(self, *args, **kwargs):
        for e in self.get_employees(
            kwargs["id"], kwargs["username"], kwargs["emailalias"]
        ):
            self.stdout.write(self.style.SUCCESS(str(e)))
            self.stdout.write(self.style.NOTICE("Member of Groups"))
            self.stdout.writelines(e.groups_add())
            self.stdout.write(self.style.WARNING("Removed from Groups"))
            self.stdout.writelines(e.groups_remove())

    def get_employees(self, ids=None, users=None, aliases=None):
        from employee.data_structures import EmployeeManager
        from employee.models import Employee

        employees = []

        if ids:
            for id in ids:
                try:
                    employees.append(
                        EmployeeManager(Employee.objects.get(employee_id=id))
                    )
                except Employee.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f"No employee with id {id}"))

        if users:
            for user in users:
                try:
                    employees.append(
                        EmployeeManager(Employee.objects.get(username=user))
                    )
                except Employee.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f"No employee with username {user}")
                    )

        if aliases:
            for alias in aliases:
                try:
                    employees.append(
                        EmployeeManager(Employee.objects.get(email_alias=alias))
                    )
                except Employee.DoesNotExist:
                    self.stderr.write(
                        self.style.ERROR(f"No employee with alias: {alias}")
                    )

        return employees
