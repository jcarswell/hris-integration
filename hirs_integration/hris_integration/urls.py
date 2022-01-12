from django.contrib import admin
from hirs_admin import urls
from django.urls import path,include


urlpatterns = [
    path('', include(urls)),
    path('admin/', admin.site.urls),
]

handler400 = urls.views.handler400
handler403 = urls.views.handler403
handler404 = urls.views.handler404
handler500 = urls.views.handler500