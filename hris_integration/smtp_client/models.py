# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.db import models


class EmailTemplates(models.Model):
    """
    The email templates that are available to be used when sending emails.
    """

    class Meta:
        db_table = "email_templates"

    #: The name of the template.
    template_name: str = models.CharField(blank=False, unique=True, max_length=64)
    #: The subject of the email. May contain jinja2 variables.
    email_subject: str = models.CharField(blank=False, max_length=78)
    #: The body of the email. The text should be in HTML format and would contain jinja2 variables.
    email_body: str = models.TextField()

    def __str__(self) -> str:
        return self.template_name
