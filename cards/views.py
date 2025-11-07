from __future__ import annotations
from typing import TYPE_CHECKING

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions
from rest_framework.exceptions import ValidationError

from cards.models import Card
from cards.serializers import CardSerializer
from common.decorators import swagger_safe_permissions
from common.permissions import (
    RelatedObjPermissionProxy,
    IsObjAdmin,
    partial_cls,
)
from generic_status.permissions import HasObjRoles
from generic_status.views import LearnMixin
from interactions.views import SaveMixin
from modules.models import Module
from modules.permissions import (
    ModuleObjIsPublic,
    ModuleObjIsOwner,
    ModuleHasViewerOrEditorRoles,
)

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.permissions import BasePermission


@extend_schema(tags=["cards"])
class CardViewSet(SaveMixin, LearnMixin, viewsets.ModelViewSet):
    serializer_class = CardSerializer

    @swagger_safe_permissions
    def get_permissions(self) -> list[BasePermission]:
        if self.action in {"retrieve", "list", "learns"}:
            return [
                (
                    ModuleObjIsPublic
                    | IsObjAdmin
                    | ModuleObjIsOwner
                    | ModuleHasViewerOrEditorRoles
                )()
            ]
        elif self.action in {"create", "update", "partial_update", "destroy"}:
            return [
                permissions.IsAuthenticated(),
                (
                    ModuleObjIsPublic
                    | partial_cls(
                        RelatedObjPermissionProxy,
                        decorated=partial_cls(HasObjRoles, roles=["editor"]),
                        model=Module,
                        lookup_url_kwarg="module_pk",
                    )
                    | IsObjAdmin
                )(),
            ]
        elif self.action == "saves":
            return [
                permissions.IsAuthenticated(),
                (
                    ModuleObjIsPublic
                    | ModuleObjIsOwner
                    | ModuleHasViewerOrEditorRoles
                    | IsObjAdmin
                )(),
            ]
        return super().get_permissions()

    def get_queryset(self) -> QuerySet:
        return Card.objects.filter(
            module_id=self.kwargs.get("module_pk")
        ).with_ann_saved(self.request.user)

    def perform_create(self, serializer: CardSerializer) -> None:
        if not (module_pk := self.kwargs.get("module_pk")):
            raise ValidationError('Missing "module_pk" parameter in URL')
        serializer.save(module_id=module_pk)
