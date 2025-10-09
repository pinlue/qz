from functools import partial

from django.db.models import Count
from rest_framework import viewsets, permissions

from abstracts.permissions import IsPublic, PublicIncludedLink
from abstracts.views import TagMixin, VisibleMixin
from common.permissions import comb_perm, IsOwner, OwnerIncludedLink
from generic_status.permissions import IsEditor, IsViewer, PermissionIncludedLink
from generic_status.views import RateMixin, PermMixin
from interactions.views import PinMixin, SaveMixin
from modules.models import Module
from modules.serializators import ModuleListSerializer, ModuleDetailSerializer, ModuleCreateUpdateSerializer


class ModuleViewSet(PinMixin, SaveMixin, TagMixin, VisibleMixin, RateMixin, PermMixin, viewsets.ModelViewSet):
    list_action_chain_links = [
        PublicIncludedLink,
        OwnerIncludedLink,
        partial(PermissionIncludedLink, model=Module, perms=["editor", "viewer"]),
    ]

    def get_queryset(self):
        qs = Module.objects.select_related("user", "topic", "lang_from", "lang_to").annotate(cards_count=Count('cards'))
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
        elif self.action == 'destroy':
            return [comb_perm(any, (permissions.IsAdminUser, IsOwner))()]
        elif self.action in {'update', 'partial_update'}:
            return [comb_perm(any, (
                permissions.IsAdminUser,
                IsOwner,
                IsEditor
            ))()]
        elif self.action in {'list'}:
            return [permissions.AllowAny()]
        elif self.action == 'retrieve':
            return [comb_perm(any, (permissions.IsAdminUser, IsOwner, IsPublic, IsEditor, IsViewer))()]
        else:
            return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
