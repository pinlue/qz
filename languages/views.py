from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.cache import cache
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.response import Response

from .cache import CACHE_LANGUAGES_KEY, CACHE_LANGUAGES_TTL
from .models import Language
from .serializers import LanguageSerializer

if TYPE_CHECKING:
    from rest_framework.request import Request
    from typing import Any


@extend_schema(tags=["languages"])
class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        cached = cache.get(CACHE_LANGUAGES_KEY)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(CACHE_LANGUAGES_KEY, response.data, CACHE_LANGUAGES_TTL)
        return response

    def get_permissions(self) -> list[permissions.BasePermission]:
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        elif self.action in {"create", "update", "partial_update", "destroy"}:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
