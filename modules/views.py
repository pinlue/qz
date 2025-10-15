from functools import partial

from django.db.models import Count
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions

from abstracts.permissions import IsObjPublic, PublicIncludedLink
from abstracts.views import TagMixin, VisibleMixin
from common.permissions import (
    IsObjOwner,
    OwnerIncludedLink,
    IsObjAdmin,
    get_accessible_q,
    partial_cls,
)
from generic_status.permissions import PermissionIncludedLink, HasObjRoles
from generic_status.views import RateMixin, PermMixin
from interactions.views import PinMixin, SaveMixin
from modules.models import Module
from modules.serializators import (
    ModuleListSerializer,
    ModuleDetailSerializer,
    ModuleCreateUpdateSerializer,
)


@extend_schema(tags=["modules"])
class ModuleViewSet(
    PinMixin,
    SaveMixin,
    TagMixin,
    VisibleMixin,
    RateMixin,
    PermMixin,
    viewsets.ModelViewSet,
):
    list_action_chain_links = [
        PublicIncludedLink,
        OwnerIncludedLink,
        partial(PermissionIncludedLink, model=Module, perms=["editor", "viewer"]),
    ]

    def get_queryset(self):
        qs = Module.objects.select_related(
            "user", "topic", "lang_from", "lang_to"
        ).annotate(cards_count=Count("cards"))
        if self.action == "retrieve":
            qs = qs.prefetch_related("cards")
        if self.action == "list":
            qs = qs.filter(get_accessible_q(self.request, self.list_action_chain_links))
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return ModuleListSerializer
        elif self.action == "retrieve":
            return ModuleDetailSerializer
        elif self.action in {"create", "update", "partial_update"}:
            return ModuleCreateUpdateSerializer
        return ModuleListSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action == "destroy":
            return [(IsObjOwner | IsObjOwner)()]
        elif self.action in {"update", "partial_update"}:
            return [
                (IsObjAdmin | IsObjOwner | partial_cls(HasObjRoles, roles=["editor"]))()
            ]
        elif self.action == "list":
            return [permissions.AllowAny()]
        elif self.action == "retrieve":
            return [
                (
                    IsObjAdmin
                    | IsObjOwner
                    | IsObjPublic
                    | partial_cls(HasObjRoles, roles=["editor", "viewer"])
                )()
            ]
        elif self.action == "rates":
            return [
                permissions.IsAuthenticated(),
                (
                    ~IsObjOwner
                    & (
                        IsObjPublic
                        | IsObjAdmin
                        | partial_cls(HasObjRoles, roles=["viewer", "editor"])
                    )
                )(),
            ]
        elif self.action in {"pins", "saves"}:
            return [
                permissions.IsAuthenticated(),
                (
                    IsObjPublic
                    | IsObjAdmin
                    | IsObjOwner
                    | partial_cls(HasObjRoles, roles=["editor", "viewer"])
                )(),
            ]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
