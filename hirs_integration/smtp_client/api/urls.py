# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from rest_framework.routers import DefaultRouter
from hris_integration.api.routers import S2Router

from . import views

router_s2 = S2Router()
router = DefaultRouter()

router.register(r'email_template', views.EmailTemplateView)
router_s2.register(r'email_template', views.S2EmailTemplateView)

app_name = 'smtp_client'
urlpatterns = router_s2.urls + router.urls