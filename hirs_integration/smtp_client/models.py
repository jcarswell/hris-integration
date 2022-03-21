# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.db import models


class EmailTemplates(models.Model):
    class Meta:
        db_table = 'email_templates'
    
    template_name = models.CharField(blank=False,unique=True,max_length=64)
    email_subject = models.CharField(blank=False,max_length=78)
    email_body = models.TextField()