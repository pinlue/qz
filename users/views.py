from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Count, Q, Prefetch
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
)
from rest_framework import mixins, viewsets, permissions

from common.exeptions import UnRegisteredPolicy
from common.permissions import get_accessible_q
from common.policy import PolicyRegistry
from folders.models import Folder
from folders.views import FolderViewSet
from modules.models import Module
from modules.views import ModuleViewSet
from users.models import User
from users.pagination import UserPagination
from users.serializers import UserPublicDetailSerializer, UserPublicSerializer

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
    pagination_class = UserPagination
    policies = PolicyRegistry()

    def get_queryset(self) -> QuerySet[User]:
        qs = User.objects.all()
        if self.action == "list":
            return qs
        if self.action == "retrieve":
            user = self.request.user
            return qs.prefetch_related(
                Prefetch(
                    "folders",
                    queryset=Folder.objects.filter(
                        get_accessible_q(
                            request=self.request,
                            links=FolderViewSet.list_action_chain_links,
                        )
                    )
                    .with_ann_saved(user)
                    .with_ann_pinned(user),
                ),
                Prefetch(
                    "modules",
                    queryset=Module.objects.filter(
                        get_accessible_q(
                            request=self.request,
                            links=ModuleViewSet.list_action_chain_links,
                        )
                    )
                    .with_ann_saved(user)
                    .with_ann_pinned(user)
                    .with_ann_perm(user)
                    .prefetch_related("tags", "cards"),
                ),
            ).annotate(
                public_modules_count=Count(
                    "modules__id",
                    filter=Q(modules__visible="public"),
                    distinct=True,
                ),
                public_folders_count=Count(
                    "folders__id",
                    filter=Q(folders__visible="public"),
                    distinct=True,
                ),
                total_cards_count=Count(
                    "modules__cards__id",
                    filter=Q(modules__visible="public"),
                    distinct=True,
                ),
            )
        return super().get_queryset()

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
