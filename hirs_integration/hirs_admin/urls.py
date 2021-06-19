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
    path('settings/config',
         views.Settings.as_view(),
         name='settings'),
    path('settings/admapping',
         views.FormView.as_view(form=forms.GroupMapping),
         name='group_mappings'),
    path('settings/patterns',
         views.FormView.as_view(form=forms.WordList),
         name='patterns'),
    path('jobs/',
         views.FormView.as_view(form=forms.JobRole),
         name='jobs'),
    path('designation/',
         views.FormView.as_view(form=forms.Designation),
         name='designations'),
    path('businessunits/',
         views.FormView.as_view(form=forms.BusinessUnit),
         name='business_units'),
    path('locations/',
         views.FormView.as_view(form=forms.Location),
         name='location'),
    path('', views.Index.as_view(), name='index')
]
