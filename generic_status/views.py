from django.contrib.contenttypes.models import ContentType
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import IsObjOwner, IsObjAdmin
from generic_status.models import Learn, Rate, Perm
from generic_status.serializers import RateSerializer, PermSerializer, LearnSerializer
from generic_status.shemas import post_relation_schema, delete_relation_schema


class BaseUserRelationMixin:
    def get_target_user(self, request, serializer):
        return request.user

    @staticmethod
    def get_queryset_filter(user, obj):
        return {
            'user': user,
            'content_type': ContentType.objects.get_for_model(obj),
            'object_id': obj.id
        }

    def _create_or_update_relation(self, user, obj, data):
        return self.get_relation_model().objects.update_or_create(
            **self.get_queryset_filter(user, obj),
            defaults=data
        )

    def _delete_relation(self, user, obj):
        qs = self.get_relation_model().objects.filter(**self.get_queryset_filter(user, obj))
        deleted, _ = qs.delete()
        return deleted

    def handle_relation_action(self, request, pk=None, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_target_user(request, serializer)
        data = serializer.validated_data

        if request.method == 'POST':
            relation, created = self._create_or_update_relation(user, obj, data)
            return Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        elif request.method == 'DELETE':
            self._delete_relation(user, obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class LearnMixin(BaseUserRelationMixin):
    @post_relation_schema(LearnSerializer)
    @delete_relation_schema()
    @action(detail=True, methods=["post", "delete"])
    def learns(self, request, pk=None, **kwargs):
        return self.handle_relation_action(request, pk, **kwargs)

    def get_permissions(self):
        if self.action == 'learns':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "learns":
            return LearnSerializer
        return super().get_serializer_class()

    def get_relation_model(self):
        if self.action == "learns":
            return Learn
        return super().get_relation_model()


class RateMixin(BaseUserRelationMixin):
    @post_relation_schema(RateSerializer)
    @delete_relation_schema()
    @action(detail=True, methods=['post', 'delete'])
    def rates(self, request, pk=None, **kwargs):
        return self.handle_relation_action(request, pk, **kwargs)

    def get_permissions(self):
        if self.action == 'rates':
            return [(~IsObjOwner)()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "rates":
            return RateSerializer
        return super().get_serializer_class()

    def get_relation_model(self):
        if self.action == "rates":
            return Rate
        return super().get_relation_model()


class PermMixin(BaseUserRelationMixin):
    @post_relation_schema(PermSerializer)
    @delete_relation_schema()
    @action(detail=True, methods=['post', 'delete'])
    def perms(self, request, pk=None, **kwargs):
        return self.handle_relation_action(request, pk, **kwargs)

    def get_permissions(self):
        if self.action == 'perms':
            return [(IsObjAdmin | IsObjOwner)()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "perms":
            return PermSerializer
        return super().get_serializer_class()

    def get_relation_model(self):
        if self.action == "perms":
            return Perm
        return super().get_relation_model()

    def get_target_user(self, request, serializer):
        if self.action == "perms":
            return serializer.validated_data['user']
        return super().get_target_user(request, serializer)
