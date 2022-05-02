# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from rest_framework.routers import DefaultRouter
from hris_integration.api.routers import S2Router

from . import views

router = DefaultRouter()

router.register(r'file-tracking', views.FileTrackingView)

app_name = 'ftp_import'
urlpatterns = router.urls