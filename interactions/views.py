from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from interactions.models import Pin, Save
from interactions.permissions import InteractionsPermsMixin
from interactions.shemas import (
    toggle_post_schema,
    toggle_delete_schema,
)

if TYPE_CHECKING:
    from django.db.models import Model
    from typing import Type
    from rest_framework.request import Request


class RelationMixin:
    def toggle(
        self, request: Request, pk: Optional[int] = None, **kwargs: dict
    ) -> Response:
        obj = self.get_object()
        content_type = ContentType.objects.get_for_model(obj)
        if request.method == "POST":
            self.get_relation_model().objects.get_or_create(
                user=request.user, content_type=content_type, object_id=obj.pk
            )
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            self.get_relation_model().objects.filter(
                user=request.user, content_type=content_type, object_id=obj.pk
            ).delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class PinMixin(RelationMixin, InteractionsPermsMixin):
    def get_relation_model(self) -> Type[Model]:
        if self.action == "pins":
            return Pin
        return super().get_relation_model()

    @toggle_post_schema
    @toggle_delete_schema
    @action(detail=True, methods=["post", "delete"], url_path="pins")
    def pins(
        self, request: Request, pk: Optional[int] = None, **kwargs: dict
    ) -> Response:
        return super().toggle(request, pk=pk)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"pins/users/(?P<user_id>\d+)",
    )
    def user_pins_list(
        self, request: Request, user_id: Optional[int] = None, **kwargs: dict
    ):
        queryset = self.filter_queryset(self.get_queryset())
        pined_queryset = queryset.filter(pins__user_id=user_id)

        serializer_class = self.get_pins_serializer_class()

        serializer = serializer_class(
            pined_queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_pins_serializer_class(self):
        if hasattr(self, "pins_serializer_class"):
            return self.pins_serializer_class
        return self.get_serializer_class()


class SaveMixin(RelationMixin, InteractionsPermsMixin):
    def get_relation_model(self) -> Type[Model]:
        if self.action == "saves":
            return Save
        return super().get_relation_model()

    def get_saves_serializer_class(self):
        if hasattr(self, "saves_serializer_class"):
            return self.saves_serializer_class
        return self.get_serializer_class()

    @toggle_post_schema
    @toggle_delete_schema
    @action(detail=True, methods=["post", "delete"], url_path="saves")
    def saves(
        self, request: Request, pk: Optional[int] = None, **kwargs: dict
    ) -> Response:
        return super().toggle(request, pk=pk)

    @action(
        detail=False,
        methods=["get"],
        url_path=r"saves/users/(?P<user_id>\d+)",
    )
    def user_saves_list(
        self, request: Request, user_id: Optional[int] = None, **kwargs: dict
    ):
        queryset = self.filter_queryset(self.get_queryset())
        saved_queryset = queryset.filter(saves__user_id=user_id)

        serializer_class = self.get_saves_serializer_class()

        serializer = serializer_class(
            saved_queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
