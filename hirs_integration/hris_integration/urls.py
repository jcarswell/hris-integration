# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

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