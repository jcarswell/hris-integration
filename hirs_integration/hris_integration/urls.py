# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.contrib import admin
from .views import errors
from django.urls import path,include,re_path
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .api.views import APIRootView

schema_view = get_schema_view(
    openapi.Info(
        title='HRIS Sync API',
        default_version='v3',
        description='API access to the HRIS Sync tool.',
        license=openapi.License(name="GNU General Public License v3.0"),
    ),
    public=True,
    permission_classes=[permissions.IsAuthenticated],
)

urlpatterns = [
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='login.html'),
         name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),

    path('', include('hirs_admin.urls')),
    path('organization/', include('organization.urls')),
    path('employee/', include('employee.urls')),
    path('smtp/', include('smtp_client.urls')),
    path('import/', include('ftp_import.urls')),
    path('software/', include('user_applications.urls')),
    path('settings/', include('settings.urls')),

    #API
    re_path(r'^api/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=86400),
            name='swagger-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=86400),
         name='swagger'),
    re_path(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='swagger-schema'),
    path('api/',APIRootView.as_view(), name='api-root'),
    path('api/employee/', include('employee.api.urls')),
    path('api/extras/', include('extras.api.urls')),
    path('api/organization/', include('organization.api.urls')),
    path('api/import/', include('ftp_import.api.urls')),
    path('api/software/', include('user_applications.api.urls')),
    path('api/smtp/', include('smtp_client.api.urls')),

    #Admin
    path('admin/', admin.site.urls),
]

handler400 = errors.handler400
handler403 = errors.handler403
handler404 = errors.handler404
handler500 = errors.handler500