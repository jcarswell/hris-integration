from hirs_integration.hirs_admin.models import JobRole
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.edit import FormView
from . import views
from . import forms

urlpatterns = [
    path('auth/login/', auth_views.LoginView.as_view(template_name='hirs_admin/login.html')),
    path('auth/logout/', auth_views.LogoutView.as_view()),
    path('employee/', views.Employee.as_view()),
    path('settings/config', views.Settings.as_view()),
    path('settings/admapping', views.FormView.as_view(form=forms.GroupMapping)),
    path('settings/patterns', views.FormView.as_view(from=forms.WordList)),
    path('jobs/', views.FormView.as_view(form=forms.JobRole)),
    path('designation/', views.FormView.as_view(from=forms.Designation)),
    path('businessunits/', views.FormView.as_view(from=forms.BusinessUnit)),
    path('locations/', views.FormView.as_view(form=forms.Location))
]
