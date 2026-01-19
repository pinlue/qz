from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import UserViewSet, UserRatingsListView

router = SimpleRouter()
router.register(r"", UserViewSet, basename="user")


base_urls = [
    path("ratings/", UserRatingsListView.as_view(), name="top-authors"),
]

urlpatterns = base_urls + router.urls