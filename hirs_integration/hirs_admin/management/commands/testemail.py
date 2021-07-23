from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "send a test email"
    requires_migrations_checks = True
    requires_system_checks = []
    
    def add_arguments(self, parser):
        parser.add_argument('dest_email', nargs='1', type=str)
    
    def handle(self, *args, **kwargs):
        from smtp_client.smtp import Smtp
        c = Smtp()
        try:
            c.send(kwargs['dest_email'],'This is a test email generated from the HRIS Intergration Tool','Test')
        except Exception as e:
            self.stderr.write(f"Failed to send email, an exception was thrown: \n{e}")
        else:
            self.stdout.write(f"Test email sent sucessfully")