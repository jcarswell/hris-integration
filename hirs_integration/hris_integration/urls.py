from django.contrib import admin
from hirs_admin import urls
from django.urls import path,include


urlpatterns = [
    path('', include(urls)),
    path('admin/', admin.site.urls),
]

