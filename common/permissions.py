from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission


class NestedPermissionMixin:
    def __init__(self, nested=False, nested_model=None, nested_lookup_url_kwarg=None):
        self.nested = nested
        self.nested_model = nested_model
        self.nested_lookup_url_kwarg = nested_lookup_url_kwarg

    def get_nested_object(self, view):
        if self.nested and self.nested_model and self.nested_lookup_url_kwarg:
            nested_id = view.kwargs.get(self.nested_lookup_url_kwarg)
            if nested_id is not None:
                return get_object_or_404(self.nested_model, id=nested_id)
        return None

    def resolve_object(self, view, obj):
        nested_obj = self.get_nested_object(view)
        return nested_obj or obj


def comb_perm(logic_func, permission_classes):
    class CombinedPermission(BasePermission):
        def has_permission(self, request, view):
            return logic_func(
                perm().has_permission(request, view)
                for perm in permission_classes
            )

        def has_object_permission(self, request, view, obj):
            return logic_func(
                perm().has_object_permission(request, view, obj)
                for perm in permission_classes
            )
    return CombinedPermission


class IsOwner(NestedPermissionMixin, BasePermission):
    def has_object_permission(self, request, view, obj):
        obj = self.resolve_object(view, obj)
        return obj.user == request.user