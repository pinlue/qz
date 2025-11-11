from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, Q, Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from abstracts.permissions import PublicIncludedLink
from abstracts.views import VisibleMixin
from common.decorators import swagger_safe_permissions
from common.exeptions import UnRegisteredPolicy
from common.permissions import (
    get_accessible_q,
    OwnerIncludedLink,
)
from common.policy import PolicyRegistry
from folders.models import Folder
from folders.serializers import (
    FolderListSerializer,
    FolderDetailSerializer,
    FolderCreateUpdateSerializer,
)
from interactions.views import PinMixin, SaveMixin
from modules.models import Module
from modules.views import ModuleViewSet

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from typing import Optional, Type
    from rest_framework.permissions import BasePermission
    from rest_framework.serializers import Serializer, ModelSerializer
    from rest_framework.request import Request


@extend_schema(tags=["folders"])
class FolderViewSet(PinMixin, SaveMixin, VisibleMixin, viewsets.ModelViewSet):
    list_action_chain_links = [PublicIncludedLink, OwnerIncludedLink]
    policies = PolicyRegistry()

    def get_queryset(self) -> QuerySet:
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
            user = self.request.user

            if self.action == "list":
                return qs.filter(
                    get_accessible_q(
                        request=self.request, links=self.list_action_chain_links
                    )
                )
            if self.action == "retrieve":
                return (
                    qs.prefetch_related(
                        Prefetch(
                            "modules",
                            queryset=Module.objects.filter(modules_q)
                            .select_related("user", "topic", "lang_from", "lang_to")
                            .with_ann_saved(user)
                            .with_ann_pinned(user)
                            .with_ann_perm(user),
                        )
                    )
                    .with_ann_saved(user)
                    .with_ann_pinned(user)
                )
        return base_qs

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return FolderListSerializer
        elif self.action == "retrieve":
            return FolderDetailSerializer
        elif self.action in {"create", "update", "partial_update"}:
            return FolderCreateUpdateSerializer
        return FolderListSerializer

    @swagger_safe_permissions
    def get_permissions(self) -> list[BasePermission]:
        try:
            return [perm() for perm in self.policies.get(self.action)]
        except UnRegisteredPolicy:
            pass
        return super().get_permissions()

    def perform_create(self, serializer: ModelSerializer) -> None:
        serializer.save(user=self.request.user)

    @extend_schema(
        methods=["POST"],
        tags=["folders"],
        parameters=[
            OpenApiParameter(
                name="pk",
                type=int,
                location="path",
            ),
            OpenApiParameter(
                name="module_id",
                type=int,
                location="path",
            ),
        ],
        responses={
            201: OpenApiResponse(response=None),
            403: OpenApiResponse(response=None),
            404: OpenApiResponse(response=None),
        },
    )
    @extend_schema(
        methods=["DELETE"],
        tags=["folders"],
        parameters=[
            OpenApiParameter(
                name="pk",
                type=int,
                location="path",
            ),
            OpenApiParameter(
                name="module_id",
                type=int,
                location="path",
            ),
        ],
        responses={
            204: OpenApiResponse(response=None),
            403: OpenApiResponse(response=None),
            404: OpenApiResponse(response=None),
        },
    )
    @action(
        detail=True,
        methods=["post", "delete"],
        url_path="modules/(?P<module_id>[^/.]+)",
    )
    def manage_module(
        self, request: Request, module_id: int, pk: Optional[int] = None
    ) -> Response:
        folder = self.get_object()
        module = get_object_or_404(Module, id=module_id)

        if request.method == "POST":
            folder.modules.add(module)
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            folder.modules.remove(module)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
