# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from django.contrib import admin
from .views import errors
from django.urls import path,include,re_path
from django.contrib.auth import views as auth_views
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from hirs_admin import urls as hris_admin_urls
from employee import urls as employee_urls
from organization import urls as organization_urls
from smtp_client import urls as smtp_client_urls
from ftp_import import urls as ftp_import_urls
from user_applications import urls as user_applications_urls

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
         auth_views.LoginView.as_view(template_name='hirs_admin/login.html'),
         name='login'),
    path('accounts/logout/',
         auth_views.LogoutView.as_view(),
         name='logout'),

    path('', include(hris_admin_urls)),
    path('/organization', include(organization_urls)),
    path('/employee', include(employee_urls)),
    path('/smtp', include(smtp_client_urls)),
    path('/import', include(ftp_import_urls)),
    path('/software', include(user_applications_urls)),

    #API
    re_path(r'^api/swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=86400),
            name='swagger-json'),
    path('api/swagger/', schema_view.with_ui('swagger', cache_timeout=86400),
         name='swagger'),
    re_path(r'^api/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='swagger-schema'),

    #Admin
    path('admin/', admin.site.urls),
]

handler400 = errors.handler400
handler403 = errors.handler403
handler404 = errors.handler404
handler500 = errors.handler500