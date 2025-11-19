from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from common.permissions import IsObjOwner, IsObjAdmin
from generic_status.models import Learn, Rate, Perm
from generic_status.serializers import RateSerializer, PermSerializer, LearnSerializer
from users.models import User

if TYPE_CHECKING:
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request
    from rest_framework.serializers import Serializer
    from django.db.models import Model
    from typing import Any, Optional, Type


class BaseUserRelationMixin:
    def get_target_user_post(self, request: Request, serializer: Serializer) -> User:
        return request.user

    def get_target_user_delete(self, request: Request, obj: Model) -> User:
        return request.user

    @staticmethod
    def get_queryset_filter(user: User, obj: Model) -> dict[str, Any]:
        return {
            "user": user,
            "content_type": ContentType.objects.get_for_model(obj),
            "object_id": obj.id,
        }

    def _create_or_update_relation(self, user: User, obj: Model, data: dict):
        defaults = self.map_validated_to_defaults(data)
        return self.get_relation_model().objects.update_or_create(
            **self.get_queryset_filter(user, obj), defaults=defaults
        )

    def _delete_relation(self, user: User, obj: Model) -> int:
        return (
            self.get_relation_model()
            .objects.filter(**self.get_queryset_filter(user, obj))
            .delete()[0]
        )

    def map_validated_to_defaults(self, validated: dict) -> dict:
        return validated

    def handle_post_action(self, request: Request) -> Response:
        obj = self.get_object()
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_target_user_post(request, serializer)
        data = serializer.validated_data

        _, created = self._create_or_update_relation(user, obj, data)
        return Response(
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

    def handle_delete_action(self, request: Request) -> Response:
        obj = self.get_object()
        user = self.get_target_user_delete(request, obj)

        self._delete_relation(user, obj)
        return Response(status=status.HTTP_204_NO_CONTENT)


class LearnMixin(BaseUserRelationMixin):
    @action(detail=True, methods=["post", "delete"])
    def learns(self, request: Request, pk: Optional[int] = None, **kwargs):
        if request.method == "POST":
            return self.handle_post_action(request)
        return self.handle_delete_action(request)

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "learns":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "learns":
            return LearnSerializer
        return super().get_serializer_class()

    def get_relation_model(self) -> Type[Model]:
        if self.action == "learns":
            return Learn
        return super().get_relation_model()


class RateMixin(BaseUserRelationMixin):
    @action(detail=True, methods=["post", "delete"])
    def rates(self, request: Request, pk: Optional[int] = None, **kwargs):
        if request.method == "POST":
            return self.handle_post_action(request)
        return self.handle_delete_action(request)

    def get_permissions(self):
        if self.action == "rates":
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
    @action(detail=True, methods=["post"])
    def perms(self, request: Request, pk: Optional[int] = None, **kwargs):
        return self.handle_post_action(request)

    @action(
        detail=True,
        methods=["delete"],
        url_path="perms/users/(?P<user_id>[^/.]+)",
        url_name="delete_perm_for_user",
    )
    def delete_perm(
        self, request: Request, pk: int = None, user_id: int = None, **kwargs
    ):
        return self.handle_delete_perm(request, user_id)

    def get_permissions(self):
        if self.action in ("perms", "delete_perm"):
            return [(IsObjAdmin | IsObjOwner)()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "perms":
            return PermSerializer
        return super().get_serializer_class()

    def get_relation_model(self):
        if self.action in ("perms", "delete_perm"):
            return Perm
        return super().get_relation_model()

    def get_target_user_post(self, request: Request, serializer: Serializer) -> User:
        if self.action == "perms":
            user = serializer.validated_data.get("user")
            if user is None:
                raise ValidationError(
                    {"user": "This field is required for perms POST."}
                )
            return user
        return super().get_target_user_post(request, serializer)

    def handle_delete_perm(self, request: Request, user_id: int) -> Response:
        obj = self.get_object()
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise ValidationError({"user": "User not found."})

        self._delete_relation(target_user, obj)
        return Response(status=status.HTTP_204_NO_CONTENT)
