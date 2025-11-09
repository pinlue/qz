from __future__ import annotations

from functools import partial
from typing import TYPE_CHECKING

from django.db.models import Count, Prefetch
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from abstracts.permissions import IsObjPublic, PublicIncludedLink
from abstracts.views import TagMixin, VisibleMixin
from cards.models import Card
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
from modules.serializers import (
    ModuleListSerializer,
    ModuleDetailSerializer,
    ModuleCreateUpdateSerializer,
    ModuleMergeSerializer,
)

if TYPE_CHECKING:
    from typing import Type
    from common.access_chain import AccessibleChain
    from django.db.models import QuerySet
    from rest_framework.serializers import Serializer, ModelSerializer
    from rest_framework.request import Request
    from rest_framework.permissions import BasePermission


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
    serializer_class = ModuleListSerializer
    list_action_chain_links: list[Type[AccessibleChain]] = [
        PublicIncludedLink,
        OwnerIncludedLink,
        partial(PermissionIncludedLink, model=Module, perms=["editor", "viewer"]),
    ]

    def get_queryset(self) -> QuerySet[Module]:
        qs = Module.objects.select_related(
            "user", "topic", "lang_from", "lang_to"
        ).annotate(cards_count=Count("cards"))
        if self.action in {"list", "retrieve"}:
            user = self.request.user
            if self.action == "retrieve":
                qs = (
                    qs.prefetch_related(
                        Prefetch(
                            "cards",
                            queryset=Card.objects.all()
                            .with_ann_saved(user)
                            .with_ann_learned(user),
                        ),
                    )
                    .with_ann_saved(user)
                    .with_ann_pinned(user)
                    .with_ann_rate(user)
                    .with_ann_perm(user)
                )
            if self.action == "list":
                qs = (
                    qs.filter(
                        get_accessible_q(self.request, self.list_action_chain_links)
                    )
                    .with_ann_saved(user)
                    .with_ann_pinned(user)
                    .with_ann_perm(user)
                )
        return qs

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "list":
            return ModuleListSerializer
        elif self.action == "retrieve":
            return ModuleDetailSerializer
        elif self.action in {"create", "update", "partial_update"}:
            return ModuleCreateUpdateSerializer
        return super().get_serializer_class()

    def get_permissions(self) -> list[BasePermission]:
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

    def perform_create(self, serializer: ModelSerializer) -> None:
        serializer.save(user=self.request.user)

    @extend_schema(request=None, responses={201: None, 404: None}, methods=["POST"])
    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            permissions.IsAuthenticated,
            IsObjPublic
            | IsObjAdmin
            | IsObjOwner
            | partial_cls(HasObjRoles, roles=["viewer", "editor"]),
        ],
    )
    def copies(self, request: Request, pk: str | None = None):
        module = self.get_object()
        module.copy(new_user=request.user)
        return Response(status=status.HTTP_201_CREATED)


@extend_schema(
    tags=["modules"],
    request=ModuleMergeSerializer,
    responses={
        201: None,
        400: OpenApiResponse(
            examples=[
                OpenApiExample(
                    "Too few modules",
                    value={"modules": ["Ensure this list has at least 2 elements."]},
                ),
                OpenApiExample(
                    "Invalid topic ID",
                    value={"topic": ["A valid integer is required."]},
                ),
            ],
        ),
        403: OpenApiResponse(
            examples=[
                OpenApiExample(
                    "Permission denied",
                    value={
                        "detail": "You do not have permission to perform this action."
                    },
                )
            ],
        ),
    },
)
class ModuleMergeView(APIView):
    def get_permissions(self) -> list[BasePermission]:
        return [
            permissions.IsAuthenticated(),
            (
                IsObjPublic
                | IsObjAdmin
                | IsObjOwner
                | partial_cls(HasObjRoles, roles=["editor", "viewer"])
            )(),
        ]

    def post(self, request: Request) -> Response:
        serializer = ModuleMergeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data["name"]
        topic = serializer.validated_data["topic"]
        modules = serializer.validated_data["modules"]

        for module in modules:
            self.check_object_permissions(request, module)

        new_module = Module.objects.create(
            name=name,
            user=request.user,
            topic=topic,
            lang_from=modules[0].lang_from,
            lang_to=modules[0].lang_to,
        )

        unique_cards = (
            Card.objects.filter(module__in=modules)
            .values("original", "translation")
            .distinct()
        )

        Card.objects.bulk_create(
            [
                Card(
                    module=new_module,
                    original=card["original"],
                    translation=card["translation"],
                )
                for card in unique_cards
            ]
        )

        return Response(status=status.HTTP_201_CREATED)
