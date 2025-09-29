from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from cards.models import Card
from cards.permissions import IsModuleOwner
from cards.serializators import CardSerializer
from common.permissions import comb_perm
from interactions.shemas import ToggleRelationSchema
from interactions.views import SaveMixin


class CardViewSet(SaveMixin, viewsets.ModelViewSet):
    serializer_class = CardSerializer

    def get_permissions(self):
        if self.action in {'retrieve', 'list'}:
            return [permissions.AllowAny()]
        elif self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [comb_perm(any, (permissions.IsAdminUser, IsModuleOwner))()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        module_pk = self.kwargs.get('module_pk')
        return Card.objects.filter(module_id=module_pk)

    def perform_create(self, serializer):
        module_pk = self.kwargs.get('module_pk')
        serializer.save(module_id=module_pk)

    @swagger_auto_schema(tags=["cards"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(tags=["cards"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(tags=["cards"])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(tags=["cards"])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["cards"])
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(tags=["cards"])
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        methods=['post', 'delete'],
        auto_schema=ToggleRelationSchema,
        request_body=no_body,
        tags=['cards']
    )
    @action(detail=True, methods=['post', 'delete'], url_path='saves')
    def saves(self, request, pk=None, **kwargs):
        return super().toggle(request, pk=pk, **kwargs)
