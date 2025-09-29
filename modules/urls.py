from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from cards.views import CardViewSet
from .views import ModuleViewSet


router = SimpleRouter()
router.register(r'modules', ModuleViewSet, basename='modules')

modules_router = routers.NestedSimpleRouter(router, r'modules', lookup='module')
modules_router.register(r'cards', CardViewSet, basename='module-cards')

urlpatterns = router.urls + modules_router.urls