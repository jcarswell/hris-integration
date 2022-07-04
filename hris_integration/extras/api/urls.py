# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from hris_integration.api.routers import HrisRouter

from . import views

router = HrisRouter()
router.APIRootView = views.ExtrasRootView

router.register("countries", views.CountriesView)
router.register("states", views.StatesView)

app_name = "extras_api"
urlpatterns = router.urls
