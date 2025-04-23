from rest_framework.routers import DefaultRouter
from .views import JobViewSet, CompanyProfileViewSet, LocationViewSet

router = DefaultRouter()
router.register('jobs', JobViewSet)
router.register('companies', CompanyProfileViewSet)
router.register('locations', LocationViewSet)

urlpatterns = router.urls
