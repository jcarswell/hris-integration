# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.api.routers import S2Router

from . import views

router_s2 = S2Router()
router_s2.APIRootView = views.EmployeeRootView

router_s2.register(r"phone_number", views.S2PhoneView)
router_s2.register(r"address", views.S2AddressView)
router_s2.register(r"employee", views.S2EmployeeView)
router_s2.register(r"source", views.S2EmployeeImportView)

app_name = "employee_s2"
urlpatterns = router_s2.urls
