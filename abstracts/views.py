from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from taggit.models import Tag

from abstracts.serializators import TagsSerializer, VisibleSerializer
from common.permissions import IsOwner, comb_perm


class TagMixin:
    @swagger_auto_schema(
        method="post",
        request_body=TagsSerializer,
        responses={
            201: "Tags added successfully",
            400: "Validation Error",
        },
    )
    @action(detail=True, methods=['post'])
    def tags(self, request, pk=None, **kwargs):
        serializer = TagsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj = self.get_object()
        tags = serializer.validated_data['tags']
        obj.tags.add(*tags)

        return Response({"tags": list(obj.tags.names())}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        method="delete",
        manual_parameters=[
            openapi.Parameter(
                "tag_id",
                openapi.IN_PATH,
                description="ID of the tag to remove",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            204: "Tag removed successfully",
            404: "Tag not found",
        },
    )
    @action(detail=True, methods=['delete'], url_path='tags/(?P<tag_id>[0-9]+)')
    def remove_tag(self, request, pk=None, tag_id=None, **kwargs):
        obj = self.get_object()
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            return Response({"error": "Tag not found"}, status=status.HTTP_404_NOT_FOUND)

        obj.tags.remove(tag)
        return Response(status=status.HTTP_204_NO_CONTENT)


class VisibleMixin:
    @swagger_auto_schema(
        method='patch',
        request_body=VisibleSerializer,
        responses={
            200: "Visibility updated successfully",
            400: "Validation error"
        },
    )
    @action(detail=True, methods=['patch'])
    def visibles(self, request, pk=None, **kwargs):
        obj = self.get_object()
        serializer = VisibleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        obj.visible = serializer.validated_data['visible']
        obj.save(update_fields=['visible'])

        return Response(status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'visibles':
            return [comb_perm(any,(
                IsOwner,
                permissions.IsAdminUser,
            ))()]
        return super().get_permissions()


