from rest_framework.routers import DefaultRouter
from .views import FolderViewSet


router = DefaultRouter()
router.register(r'', FolderViewSet)

urlpatterns = router.urls