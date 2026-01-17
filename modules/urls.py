from django.urls import path
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.routers import DefaultRouter

from io_manager.views import GenericImportView, GenericExportView
from .io import ModuleCardsImporter, ModuleCardsExporter
from .models import Module
from .views import ModuleViewSet, ModuleMergeView

router = DefaultRouter()
router.register(r"modules", ModuleViewSet, basename="modules")

generic_urls = [
    path(
        "modules/<int:pk>/import/",
        extend_schema_view(post=extend_schema(tags=["modules"]))(
            GenericImportView.as_view(
                strategy=ModuleCardsImporter,
                model=Module,
            )
        ),
        name="module-cards-import",
    ),
    path(
        "modules/<int:pk>/export/",
        extend_schema_view(get=extend_schema(tags=["modules"]))(
            GenericExportView.as_view(
                strategy=ModuleCardsExporter,
                model=Module,
            )
        ),
        name="module-cards-export",
    ),
]

module_merge_urls = [
    path("modules/merge/", ModuleMergeView.as_view(), name="modules-merge"),
]

urlpatterns = module_merge_urls + generic_urls + router.urls
