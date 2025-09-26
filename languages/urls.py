from rest_framework.routers import DefaultRouter
from .views import LanguageViewSet

router = DefaultRouter()
router.register(r'', LanguageViewSet)

urlpatterns = router.urls