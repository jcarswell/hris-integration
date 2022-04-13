# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.urls import path
from hris_integration.views import ListView

from . import views
from . import forms

urlpatterns = [
    path('employee/',
         views.Employee.as_view(),
         name='employee'),
    path('employee/<int:id>/',
         views.Employee.as_view(),
         name='employee_edit'),
    path('pending/',
         ListView.as_view(form=forms.EmployeePending),
         name='employee_pending'),
    path('pending/<int:id>/',
         views.PendingEmployeeEdit.as_view(),
         name='employee_pending_edit'),
    path('manual/<int:id>/',
         views.ManualImport.as_view(),
         name='employee_manual')
]