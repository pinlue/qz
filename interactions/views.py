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


class SaveMixin(RelationMixin, InteractionsPermsMixin):
    def get_relation_model(self) -> Type[Model]:
        if self.action == "saves":
            return Save
        return super().get_relation_model()

    @toggle_post_schema
    @toggle_delete_schema
    @action(detail=True, methods=["post", "delete"], url_path="saves")
    def saves(
        self, request: Request, pk: Optional[int] = None, **kwargs: dict
    ) -> Response:
        return super().toggle(request, pk=pk)
