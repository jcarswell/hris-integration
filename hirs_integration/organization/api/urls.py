# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from hris_integration.api.routers import HrisRouter

from . import views

router = HrisRouter()
router.APIRootView = views.OrganizationRootView
router.register(r'business_unit', views.BusinessUnitView)
router.register(r'job_role', views.JobRoleView)
router.register(r'location', views.LocationView)
router.register(r'group_mapping', views.GroupMappingView)

app_name = 'organization_api'
urlpatterns = router.urls