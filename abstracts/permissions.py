from rest_framework.permissions import BasePermission

from abstracts.models import Visible
from common.permissions import NestedPermissionMixin


class IsPublic(NestedPermissionMixin, BasePermission):
    def has_object_permission(self, request, view, obj):
        obj = self.resolve_object(view, obj)
        return getattr(obj, "visible", None) == Visible.Status.PUBLIC