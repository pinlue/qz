from rest_framework.permissions import BasePermission


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


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user