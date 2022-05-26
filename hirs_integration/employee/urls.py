# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from django.urls import path
from hris_integration.views import ListView, FormView

from . import views
from . import forms

urlpatterns = [
    path("employee/", views.Employee.as_view(), name="employee"),
    path("employee/<int:id>/", views.Employee.as_view(), name="employee_edit"),
    path("new/", FormView.as_view(form=forms.NewEmployeeForm), name="employee_new"),
    path(
        "imported/",
        ListView.as_view(form=forms.ImportedEmployeeView),
        name="employee_imported_list",
    ),
    path(
        "imported/",
        FormView.as_view(form=forms.ImportedEmployeeView),
        name="employee_imported_edit",
    ),
    path(
        "manual/<int:id>/",
        views.ManualImport.as_view(),
        name="employee_manual",
    ),
]
