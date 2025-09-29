from django.db.models import Count
from rest_framework import viewsets, permissions

from common.permissions import comb_perm, IsOwner
from interactions.views import PinMixin, SaveMixin
from modules.models import Module
from modules.serializators import ModuleListSerializer, ModuleDetailSerializer, ModuleCreateUpdateSerializer


class ModuleViewSet(PinMixin, SaveMixin, viewsets.ModelViewSet):
    queryset = Module.objects.all()

    def get_queryset(self):
        qs = Module.objects.annotate(cards_count=Count('cards'))
        if self.action == 'retrieve':
            qs = qs.prefetch_related('cards')
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return ModuleListSerializer
        elif self.action == 'retrieve':
            return ModuleDetailSerializer
        elif self.action in {'create', 'update', 'partial_update'}:
            return ModuleCreateUpdateSerializer
        return ModuleListSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [comb_perm(any, (
                permissions.IsAdminUser,
                IsOwner,
            ))]
        elif self.action in {'list', 'retrieve'}:
            return [permissions.AllowAny()]
        else:
            return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
