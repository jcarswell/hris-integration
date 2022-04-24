from rest_framework.routers import DefaultRouter
from hris_integration.api.routers import S2Router

from . import views

router_s2 = S2Router()
router = DefaultRouter()

router_s2.register(r'business_unit', views.S2BusinessUnitView)
router_s2.register(r'job_role', views.S2JobRoleView)
router_s2.register(r'location', views.S2LocationView)

router.register(r'business_unit', views.BusinessUnitView)
router.register(r'job_role', views.JobRoleView)
router.register(r'location', views.LocationView)
router.register(r'group_mapping', views.GroupMappingView)

app_name = 'organization'
urlpatterns = router_s2.urls + router.urls