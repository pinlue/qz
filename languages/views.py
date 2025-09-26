from rest_framework import viewsets, permissions
from .models import Language
from .serializators import LanguageSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = Language.objects.all()
    serializer_class = LanguageSerializer

    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]



