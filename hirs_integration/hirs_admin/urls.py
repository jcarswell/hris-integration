from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from . import forms

urlpatterns = [
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='hirs_admin/login.html'),
         name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),
    path('employee/',
         views.Employee.as_view(),
         name='employee'),
    path('employee/<int:id>/',
         views.Employee.as_view(),
         name='employee_edit'),
    path('settings/config/',
         views.Settings.as_view(),
         name='settings'),
    path('settings/admapping/',
         views.ListView.as_view(form=forms.GroupMapping),
         name='group_mappings'),
    path('settings/admapping/<int:id>/',
         views.FormView.as_view(form=forms.GroupMapping),
         name='group_mappings_edit'),
    path('settings/patterns/',
         views.ListView.as_view(form=forms.WordList),
         name='patterns'),
    path('settings/patterns/<int:id>/',
         views.FormView.as_view(form=forms.WordList),
         name='patterns_edit'),
    path('jobs/',
         views.ListView.as_view(form=forms.JobRole),
         name='jobs'),
    path('jobs/<int:id>/',
         views.FormView.as_view(form=forms.JobRole),
         name='jobs_edit'),
    path('designation/',
         views.ListView.as_view(form=forms.Designation),
         name='designations'),
    path('businessunits/',
         views.ListView.as_view(form=forms.BusinessUnit),
         name='business_units'),
    path('businessunits/<int:id>/',
         views.FormView.as_view(form=forms.BusinessUnit),
         name='business_units_edit'),
    path('locations/',
         views.ListView.as_view(form=forms.Location),
         name='location'),
    path('locations/<int:id>/',
         views.FormView.as_view(form=forms.Location),
         name='location_edit'),
    path('employee_pending/',
         views.ListView.as_view(form=forms.EmployeePending),
         name='pending'),
    path('employee_pending/<int:id>/',
         views.FormView.as_view(form=forms.EmployeePending),
         name='pending_edit'),
    path('',
         views.Index.as_view(),
         name='index'),
    path('pending_import/',
         views.CsvImport.as_view(),
         name="pending_import"),
    path('actions/',
         views.JobActions.as_view(),
         name='actions'),
    path('actions/<str:job>',
          views.JobActions.as_view(),
         name='actions_go'),
]
