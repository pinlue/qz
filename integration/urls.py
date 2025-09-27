from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DeepLApiKeyViewSet, DeepLTranslationsView


router = DefaultRouter()
router.register(r'', DeepLApiKeyViewSet)
urlpatterns = [
    path("translations/", DeepLTranslationsView.as_view(), name="deepl-translate"),
] + router.urls