from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import BasePermission

from common.permissions import NestedPermissionMixin
from generic_status.models import Perm


class BaseRolePermission(NestedPermissionMixin, BasePermission):
    role = None

    def get_content_type(self, obj):
        return ContentType.objects.get_for_model(obj.__class__)

    def has_object_permission(self, request, view, obj):
        if self.role is None:
            return False
        obj = self.resolve_object(view, obj)
        ct = self.get_content_type(obj)
        return Perm.objects.filter(
            user=request.user,
            object_id=obj.id,
            perm=self.role,
            content_type=ct
        ).exists()


class IsEditor(BaseRolePermission):
    role = Perm.Status.EDITOR


class IsViewer(BaseRolePermission):
    role = Perm.Status.VIEWER


