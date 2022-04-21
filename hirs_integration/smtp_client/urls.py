# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.urls import path
from hris_integration.views import FormView,ListView

from . import forms

urlpatterns = [
    path('settings/email_templates/<int:id>/',
        FormView.as_view(form=forms.EmailTemplate,
        template_name='hirs_admin/tinymce_edit.html'),
        name='email_template_edit'),
    path('settings/email_templates/',
        ListView.as_view(form=forms.EmailTemplate),
        name='email_template'),
]