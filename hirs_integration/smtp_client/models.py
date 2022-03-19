from django.db import models


class EmailTemplates(models.Model):
    class Meta:
        db_table = 'email_templates'
    
    template_name = models.CharField(blank=False,unique=True,max_length=64)
    email_subject = models.CharField(blank=False,max_length=78)
    email_body = models.TextField()