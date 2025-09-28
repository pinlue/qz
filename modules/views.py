from rest_framework import viewsets, permissions

from common.permissions import comb_perm, IsOwner
from modules.models import Module
from modules.serializators import ModuleListSerializer, ModuleDetailSerializer, ModuleCreateUpdateSerializer


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()

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
