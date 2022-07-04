# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.api.routers import HrisRouter

from . import views

router = HrisRouter()
router.APIRootView = views.EmployeeRootView

router.register(r"phone_number", views.PhoneView)
router.register(r"address", views.AddressView)
router.register(r"employee", views.EmployeeView)
router.register(r"source", views.EmployeeImportView)

app_name = "employee_api"
urlpatterns = router.urls
