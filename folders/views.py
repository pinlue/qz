from django.db.models import Count, Q, Prefetch
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from abstracts.permissions import IsObjPublic, PublicIncludedLink
from abstracts.views import VisibleMixin
from common.permissions import (
    IsObjOwner,
    get_accessible_q,
    IsObjAdmin,
    partial_cls,
)
from folders.models import Folder
from folders.serializators import (
    FolderListSerializer,
    FolderDetailSerializer,
    FolderCreateUpdateSerializer,
)
from interactions.views import PinMixin, SaveMixin
from modules.models import Module
from modules.permissions import (
    ModuleObjIsPublic,
    ModuleObjIsOwner,
    ModuleHasViewerOrEditorRoles,
)
from modules.views import ModuleViewSet


class FolderViewSet(PinMixin, SaveMixin, VisibleMixin, viewsets.ModelViewSet):
    list_action_chain_links = [PublicIncludedLink]

    def get_queryset(self):
        base_qs = Folder.objects.select_related("user")

        if self.action in {"list", "retrieve"}:
            modules_q = get_accessible_q(
                self.request, ModuleViewSet.list_action_chain_links
            )
            qs = base_qs.annotate(
                modules_count=Count(
                    "modules",
                    filter=Q(modules__in=Module.objects.filter(modules_q)),
                    distinct=True,
                )
            )
            if self.action == "list":
                return qs.filter(
                    get_accessible_q(
                        request=self.request, links=self.list_action_chain_links
                    )
                )
            if self.action == "retrieve":
                return qs.prefetch_related(
                    Prefetch(
                        "modules",
                        queryset=Module.objects.filter(modules_q).select_related(
                            "user", "topic", "lang_from", "lang_to"
                        ),
                    )
                )
        return base_qs

    def get_serializer_class(self):
        if self.action == "list":
            return FolderListSerializer
        elif self.action == "retrieve":
            return FolderDetailSerializer
        elif self.action in {"create", "update", "partial_update"}:
            return FolderCreateUpdateSerializer
        return FolderListSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [(IsObjAdmin | IsObjOwner)()]
        elif self.action == "list":
            return [permissions.AllowAny()]
        elif self.action == "retrieve":
            return [(IsObjAdmin | IsObjOwner | IsObjPublic)()]
        elif self.action == "pins":
            return [
                permissions.IsAuthenticated(),
                (IsObjAdmin | IsObjOwner | IsObjPublic)(),
            ]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        methods=["post", "delete"],
        manual_parameters=[
            openapi.Parameter(
                "module_id", openapi.IN_PATH, type=openapi.TYPE_INTEGER, required=True
            )
        ],
        request_body=no_body,
        responses={
            201: openapi.Response("Module added to folder"),
            204: openapi.Response("Module removed from folder"),
            400: openapi.Response("Bad request"),
            404: openapi.Response("Module not found"),
            405: openapi.Response("Method not allowed"),
        },
    )
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="modules/(?P<module_id>[^/.]+)",
        permission_classes=[
            IsObjAdmin
            | (
                IsObjOwner
                & (ModuleObjIsPublic | ModuleObjIsOwner | ModuleHasViewerOrEditorRoles)
            )
        ],
    )
    def manage_module(self, request, pk=None, module_id=None):
        folder = self.get_object()
        module = get_object_or_404(Module, id=module_id)

        if request.method == "POST":
            folder.modules.add(module)
            return Response({"status": "module added"}, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            folder.modules.remove(module)
            return Response(
                {"status": "module removed"}, status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"error": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
