from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from cards.views import CardViewSet
from io_manager.views import GenericImportView, GenericExportView
from .io import ModuleCardsImporter, ModuleCardsExporter
from .models import Module
from .views import ModuleViewSet


router = SimpleRouter()
router.register(r'modules', ModuleViewSet, basename='modules')

modules_router = routers.NestedSimpleRouter(router, r'modules', lookup='module')
modules_router.register(r'cards', CardViewSet, basename='module-cards')

generic_urls = [
    path(
        'modules/<int:pk>/import/',
        GenericImportView.as_view(
            strategy=ModuleCardsImporter,
            model=Module,
        ),
        name='module-cards-import'
    ),
    path(
        'modules/<int:pk>/export/',
        GenericExportView.as_view(
            strategy=ModuleCardsExporter,
            model=Module,
        ),
        name='module-cards-export'
    ),
]

urlpatterns = generic_urls + router.urls + modules_router.urls
