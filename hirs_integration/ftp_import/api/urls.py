# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.routers import HrisRouter

from . import views

router = HrisRouter()

router.register(r'file-tracking', views.FileTrackingView)

app_name = 'ftp_import'
urlpatterns = router.urls