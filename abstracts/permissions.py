from django.db.models import Q
from rest_framework.permissions import BasePermission

from abstracts.models import Visible
from common.access_chain import AccessibleChain
from common.permissions import NestedPermissionMixin


class IsPublic(NestedPermissionMixin, BasePermission):
    def has_object_permission(self, request, view, obj):
        obj = self.resolve_object(view, obj)
        return getattr(obj, "visible", None) == Visible.Status.PUBLIC


class PublicIncludedLink(AccessibleChain):
    def handle(self, q=None):
        if q is None:
            q = Q()

        q |= Q(visible=Visible.Status.PUBLIC)
        return super().handle(q)