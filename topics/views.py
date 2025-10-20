from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import viewsets, permissions
from .models import Topic
from .serializers import TopicSerializer


@extend_schema(tags=["topics"])
class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer

    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            return [permissions.AllowAny()]
        elif self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [permissions.IsAdminUser()]
        return super().get_permissions()
