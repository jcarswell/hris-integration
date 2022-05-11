# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.routers import S2Router,HrisRouter

from . import views

router = HrisRouter()
router_s2 = S2Router()

router_s2.register('countries', views.CountriesView)
router_s2.register('states', views.StatesView)

router.register('countries', views.CountriesView)
router.register('states', views.StatesView)

app_name = 'extras'
urls = router.urls + router_s2.urls