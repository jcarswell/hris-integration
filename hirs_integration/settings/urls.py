# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.urls import path
from hris_integration.views import FormView,ListView


from . import views
from . import forms

urlpatterns = [
    path('config/',
         views.Settings.as_view(),
         name='settings'),
    path('patterns/',
         ListView.as_view(form=forms.WordList),
         name='patterns'),
    path('patterns/<int:id>/',
         FormView.as_view(form=forms.WordList),
         name='patterns_edit'),
]