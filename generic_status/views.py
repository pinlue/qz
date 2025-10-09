from django.contrib.contenttypes.models import ContentType
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import comb_perm, IsOwner
from generic_status.models import Learn, Rate, Perm
from generic_status.serializators import RateSerializer, PermSerializer, LearnSerializer


class BaseUserRelationMixin:
    relation_model = None
    serializer_class = None

    def get_relation_queryset(self, obj):
        return self.relation_model.objects.filter(
            user=self.request.user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id
        )

    def add_relation(self, request, pk=None, **kwargs):
        obj = self.get_object()
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        relation, created = self.relation_model.objects.update_or_create(
            user=request.user,
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            defaults=serializer.validated_data
        )

        return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def remove_relation(self, request, pk=None, **kwargs):
        obj = self.get_object()
        qs = self.get_relation_queryset(obj)
        deleted, _ = qs.delete()
        if deleted:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "Relation not found"}, status=status.HTTP_404_NOT_FOUND)

    def handle_relation_action(self, request, pk=None, **kwargs):
        if request.method == 'POST':
            return self.add_relation(request, pk, **kwargs)
        elif request.method == 'DELETE':
            return self.remove_relation(request, pk, **kwargs)


class LearnMixin(BaseUserRelationMixin):
    relation_model = Learn
    serializer_class = LearnSerializer

    @swagger_auto_schema(
        method="post",
        request_body=LearnSerializer,
        responses={
            201: openapi.Response("Created"),
            200: openapi.Response("Updated"),
        },
    )
    @swagger_auto_schema(
        method="delete",
        responses={
            204: openapi.Response("Deleted"),
            404: openapi.Response("Relation not found"),
        },
    )
    @action(detail=True, methods=['post', 'delete'])
    def learns(self, request, pk=None, **kwargs):
        return self.handle_relation_action(request, pk, **kwargs)


class RateMixin(BaseUserRelationMixin):
    relation_model = Rate
    serializer_class = RateSerializer

    @swagger_auto_schema(
        method="post",
        request_body=RateSerializer,
        responses={
            201: openapi.Response("Created"),
            200: openapi.Response("Updated"),
        },
    )
    @swagger_auto_schema(
        method="delete",
        responses={
            204: openapi.Response("Deleted"),
            404: openapi.Response("Relation not found"),
        },
    )
    @action(detail=True, methods=['post', 'delete'])
    def rates(self, request, pk=None, **kwargs):
        return self.handle_relation_action(request, pk, **kwargs)


class PermMixin(BaseUserRelationMixin):
    relation_model = Perm
    serializer_class = PermSerializer

    def get_permissions(self):
        if self.action == 'perms':
            return [comb_perm(any, (permissions.IsAdminUser, IsOwner))()]
        return super().get_permissions()

    @swagger_auto_schema(
        method="post",
        request_body=PermSerializer,
        responses={
            201: openapi.Response("Created"),
            200: openapi.Response("Updated"),
        },
    )
    @swagger_auto_schema(
        method="delete",
        responses={
            204: openapi.Response("Deleted"),
            404: openapi.Response("Relation not found"),
        },
    )
    @action(detail=True, methods=['post', 'delete'])
    def perms(self, request, pk=None, **kwargs):
        return self.handle_relation_action(request, pk, **kwargs)