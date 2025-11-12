from __future__ import annotations

from typing import TYPE_CHECKING

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)
from rest_framework import mixins, viewsets, permissions

from common.exeptions import UnRegisteredPolicy
from common.policy import PolicyRegistry
from users.filters import UserFilter
from users.models import User
from users.pagination import UserPagination
from users.serializers import UserPublicDetailSerializer, UserPublicSerializer
from users.service import UserService

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.serializers import Serializer
    from typing import Type


@extend_schema_view(
    list=extend_schema(
        responses={
            200: OpenApiResponse(
                response=UserPublicSerializer,
            ),
        },
    ),
    retrieve=extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                required=True,
                type=int,
                location="path",
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=UserPublicDetailSerializer,
            ),
            404: None,
        },
    ),
    destroy=extend_schema(
        parameters=[
            OpenApiParameter(
                name="id",
                required=True,
                type=int,
                location="path",
            ),
        ],
        responses={
            204: None,
            403: None,
            404: None,
        },
    ),
)
@extend_schema(tags=["users"])
class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    filter_backends = [DjangoFilterBackend]
    filterset_class = UserFilter
    pagination_class = UserPagination
    policies = PolicyRegistry()

    def get_queryset(self) -> QuerySet[User]:
        service = UserService(
            request=self.request,
            action=self.action,
        )
        return service.get_queryset()

    def get_permissions(self) -> list[permissions.BasePermission]:
        try:
            return [perm() for perm in self.policies.get(self.action)]
        except UnRegisteredPolicy:
            pass
        return super().get_permissions()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "retrieve":
            return UserPublicDetailSerializer
        if self.action == "list":
            return UserPublicSerializer
        return super().get_serializer_class()
