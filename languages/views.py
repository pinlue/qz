from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from .models import Language
from .serializers import LanguageSerializer


@extend_schema(tags=["languages"])
class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    def get_permissions(self) -> list[permissions.BasePermission]:
        if self.action in {"list", "retrieve"}:
            return [permissions.AllowAny()]
        elif self.action in {"create", "update", "partial_update", "destroy"}:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
