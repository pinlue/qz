from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from taggit.models import Tag

from abstracts.serializators import TagsSerializer, VisibleSerializer
from common.permissions import IsObjOwner, IsObjAdmin


class TagMixin:
    @extend_schema(
        request=TagsSerializer,
        responses={
            201: None,
            400: None,
        },
    )
    @action(detail=True, methods=['post'])
    def tags(self, request, pk=None, **kwargs):
        serializer = TagsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = self.get_object()
        tags = serializer.validated_data['tags']
        obj.tags.add(*tags)

        return Response(status=status.HTTP_201_CREATED)


    @extend_schema(
        methods=["DELETE"],
        parameters=[
            OpenApiParameter(
                name="tag_id",
                location='path',
                type=int,
                required=True,
            )
        ],
        responses={
            204: None,
            404: None,
        }
    )
    @action(detail=True, methods=["delete"], url_path="tags/(?P<tag_id>[0-9]+)")
    def remove_tag(self, request, pk=None, tag_id=None, **kwargs):
        obj = self.get_object()
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        obj.tags.remove(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        if self.action in {'tags', 'remove_tag'}:
            return [(IsObjOwner | IsObjAdmin)()]
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
    def visibles(self, request, pk=None, **kwargs):
        obj = self.get_object()
        serializer = VisibleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj.visible = serializer.validated_data['visible']
        obj.save(update_fields=['visible'])

        return Response(status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'visibles':
            return [(IsObjOwner | IsObjAdmin)()]
        return super().get_permissions()
