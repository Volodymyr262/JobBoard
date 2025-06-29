from rest_framework.routers import DefaultRouter
from .views import JobViewSet, CompanyProfileViewSet, LocationViewSet, SavedJobViewSet

router = DefaultRouter()
router.register('jobs', JobViewSet)
router.register('companies', CompanyProfileViewSet)
router.register('locations', LocationViewSet)
router.register(r'saved-jobs', SavedJobViewSet, basename='saved-jobs')

urlpatterns = router.urls
