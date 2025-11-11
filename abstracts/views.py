from __future__ import annotations

from typing import TYPE_CHECKING

from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from taggit.models import Tag

from abstracts.serializers import TagsSerializer, VisibleSerializer
from common.permissions import IsObjOwner, IsObjAdmin

if TYPE_CHECKING:
    from rest_framework.request import Request
    from typing import Any
    from rest_framework.permissions import BasePermission


class TagMixin:
    @extend_schema(
        request=TagsSerializer,
        responses={
            201: None,
            400: None,
        },
    )
    @action(detail=True, methods=["post"])
    def tags(self, request: Request, pk: str | None = None, **kwargs: Any) -> Response:
        serializer = TagsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = self.get_object()
        tags = serializer.validated_data["tags"]
        obj.tags.add(*tags)

        return Response(status=status.HTTP_201_CREATED)

    @extend_schema(
        methods=["DELETE"],
        parameters=[
            OpenApiParameter(
                name="tag_name",
                location="path",
                type=str,
                required=True,
            )
        ],
        responses={
            204: None,
            404: None,
        },
    )
    @action(detail=True, methods=["delete"], url_path="tags/(?P<tag_name>[^/]+)")
    def remove_tag(
        self, request: Request, tag_name: str, pk: str | None = None, **kwargs: Any
    ) -> Response:
        obj = self.get_object()

        try:
            tag = Tag.objects.get(name=tag_name)
        except Tag.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

        obj.tags.remove(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self) -> list[BasePermission]:
        if self.action in {"tags", "remove_tag"}:
            return [permissions.IsAuthenticated(), (IsObjOwner | IsObjAdmin)()]
        return super().get_permissions()


class VisibleMixin:
    @extend_schema(
        request=VisibleSerializer,
        responses={
            200: None,
            400: None,
        },
        methods=["PATCH"],
    )
    @action(detail=True, methods=["patch"])
    def visibles(
        self, request: Request, pk: str | None = None, **kwargs: Any
    ) -> Response:
        obj = self.get_object()
        serializer = VisibleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj.visible = serializer.validated_data["visible"]
        obj.save(update_fields=["visible"])

        return Response(status=status.HTTP_200_OK)

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "visibles":
            return [permissions.IsAuthenticated(), (IsObjOwner | IsObjAdmin)()]
        return super().get_permissions()
