# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.forms import Form,MetaBase
from django.utils.translation import gettext_lazy as _t

from smtp_client import models

class EmailTemplate(Form):
    name = _t("Email Template")
    list_fields = ['template_name']

    class Meta(MetaBase):
        model = models.EmailTemplates
        fields = ['template_name','email_subject','email_body']
        disable = ('template_name')
        labels = {
            'template_name': _t('Template Name'),
            'email_subject': _t('Subject'),
            'email_body': _t('Body'),
        }