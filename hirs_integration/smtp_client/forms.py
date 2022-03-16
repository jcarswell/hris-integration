from hirs_admin.forms.base_model_form import Form
from django.utils.translation import gettext_lazy as _t

from smtp_client import models

class EmailTemplate(Form):
    list_fields = ['template_name']
    
    class Meta:
        model = models.EmailTemplates
        fields = ['template_name','email_subject','email_body']
        disable = ('template_name')
        labels = {
            'template_name': _t('Template Name'),
            'email_subject': _t('Subject'),
            'email_body': _t('Body'),
        }