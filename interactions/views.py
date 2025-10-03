from django.contrib.contenttypes.models import ContentType
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from interactions.models import Pin, Save
from interactions.permissions import InteractionsPermsMixin
from interactions.shemas import ToggleRelationSchema


class RelationMixin:
    relation_model = None

    def toggle(self, request, pk=None, **kwargs):
        obj = self.get_object()
        content_type = ContentType.objects.get_for_model(obj)
        if request.method == 'POST':
            self.relation_model.objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=obj.pk
            )
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            self.relation_model.objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.pk
            ).delete()
            return Response(status=status.HTTP_200_OK)


class PinMixin(RelationMixin, InteractionsPermsMixin):
    relation_model = Pin

    @swagger_auto_schema(methods=['post', 'delete'], auto_schema=ToggleRelationSchema, request_body=no_body)
    @action(detail=True, methods=['post', 'delete'], url_path='pins')
    def pins(self, request, pk=None, **kwargs):
        return super().toggle(request, pk=pk)

class SaveMixin(RelationMixin, InteractionsPermsMixin):
    relation_model = Save

    @swagger_auto_schema(methods=['post', 'delete'], auto_schema=ToggleRelationSchema, request_body=no_body)
    @action(detail=True, methods=['post', 'delete'], url_path='saves')
    def saves(self, request, pk=None, **kwargs):
        return super().toggle(request, pk=pk)