from __future__ import annotations

from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
)
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from abstracts.views import VisibleMixin
from common.decorators import swagger_safe_permissions
from common.exeptions import UnRegisteredPolicy
from common.policy import PolicyRegistry

from folders.pagination import FolderPagination
from folders.serializers import (
    FolderListSerializer,
    FolderDetailSerializer,
    FolderCreateUpdateSerializer,
)
from folders.service import FolderService
from interactions.views import PinMixin, SaveMixin
from modules.models import Module
from .filters import FolderFilter

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from typing import Optional, Type
    from rest_framework.permissions import BasePermission
    from rest_framework.serializers import Serializer, ModelSerializer
    from rest_framework.request import Request
    from .models import Folder


@extend_schema(tags=["folders"])
class FolderViewSet(PinMixin, SaveMixin, VisibleMixin, viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = FolderFilter
    pagination_class = FolderPagination
    policies = PolicyRegistry()

    def get_queryset(self) -> QuerySet[Folder]:
        service = FolderService(
            request=self.request,
            action=self.action,
        )
        return service.get_queryset()

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
