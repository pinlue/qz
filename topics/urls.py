from rest_framework.routers import DefaultRouter
from .views import TopicViewSet

router = DefaultRouter()
router.register(r'', TopicViewSet)

urlpatterns = router.urls