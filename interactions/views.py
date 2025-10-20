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


class RelationMixin:
    def toggle(self, request, pk=None, **kwargs):
        obj = self.get_object()
        content_type = ContentType.objects.get_for_model(obj)
        if request.method == 'POST':
            self.get_relation_model().objects.get_or_create(
                user=request.user,
                content_type=content_type,
                object_id=obj.pk
            )
            return Response(status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            self.get_relation_model().objects.filter(
                user=request.user,
                content_type=content_type,
                object_id=obj.pk
            ).delete()
            return Response(status=status.HTTP_200_OK)


class PinMixin(RelationMixin, InteractionsPermsMixin):
    def get_relation_model(self):
        if self.action == "pins":
            return Pin
        return super().get_relation_model()

    @toggle_post_schema
    @toggle_delete_schema
    @action(detail=True, methods=["post", "delete"], url_path="pins")
    def pins(self, request, pk=None, **kwargs):
        return super().toggle(request, pk=pk)

class SaveMixin(RelationMixin, InteractionsPermsMixin):

    def get_relation_model(self):
        if self.action == "saves":
            return Save
        return super().get_relation_model()

    @toggle_post_schema
    @toggle_delete_schema
    @action(detail=True, methods=["post", "delete"], url_path="saves")
    def saves(self, request, pk=None, **kwargs):
        return super().toggle(request, pk=pk)
