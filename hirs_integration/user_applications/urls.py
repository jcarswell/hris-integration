# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.urls import path
from hris_integration.views import FormView,ListView

from . import forms

urlpatterns = [
    path('software/<int:id>/',
         FormView.as_view(form=forms.Software),
         name='software_edit'),
    path('software/',
         ListView.as_view(form=forms.Software),
         name='software'),
    path('accounts/<int:id>/',
         FormView.as_view(form=forms.Account),
         name='accounts_edit'),
    path('accounts/',
         ListView.as_view(form=forms.Account),
         name='accounts'),
]