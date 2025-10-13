from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, permissions
from rest_framework.decorators import action

from abstracts.permissions import IsObjPublic
from cards.models import Card
from cards.serializators import CardSerializer
from common.permissions import (
    RelatedObjPermissionProxy,
    IsObjOwner,
    IsObjAdmin,
    partial_cls,
)
from generic_status.permissions import HasObjRoles
from generic_status.serializators import LearnSerializer
from generic_status.views import LearnMixin
from interactions.shemas import ToggleRelationSchema
from interactions.views import SaveMixin
from modules.models import Module
from modules.permissions import (
    ModuleObjIsPublic,
    ModuleObjIsOwner,
    ModuleHasViewerOrEditorRoles,
)


class CardViewSet(SaveMixin, LearnMixin, viewsets.ModelViewSet):
    serializer_class = CardSerializer

    def get_permissions(self):
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

    def get_queryset(self):
        return Card.objects.filter(module_id=self.kwargs.get("module_pk"))

    def perform_create(self, serializer):
        module_pk = self.kwargs.get("module_pk")
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
        methods=["post", "delete"],
        auto_schema=ToggleRelationSchema,
        request_body=no_body,
        tags=["cards"],
    )
    @action(detail=True, methods=["post", "delete"], url_path="saves")
    def saves(self, request, pk=None, **kwargs):
        return super().toggle(request, pk=pk, **kwargs)

    @swagger_auto_schema(
        method="post",
        request_body=LearnSerializer,
        responses={
            201: openapi.Response("Created"),
            200: openapi.Response("Updated"),
        },
        tags=["cards"],
    )
    @swagger_auto_schema(
        method="delete",
        responses={
            204: openapi.Response("Deleted"),
            404: openapi.Response("Relation not found"),
        },
        tags=["cards"],
    )
    @action(detail=True, methods=["post", "delete"])
    def learns(self, request, pk=None, **kwargs):
        return super().learns(request, pk=pk, **kwargs)
