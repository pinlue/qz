from django.db.models import Q
from rest_framework.permissions import BasePermission

from common.access_chain import AccessibleChain
from common.decorators import login_required_link


class RelatedPermissionProxy:
    def __init__(self, decorated, model, lookup_url_kwarg, *args, **kwargs):
        self.decorated_instance = decorated(*args, **kwargs)
        self.model = model
        self.lookup_url_kwarg = lookup_url_kwarg

    def has_permission(self, request, view):
        return self.decorated_instance.has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        nested_id = view.kwargs.get(self.lookup_url_kwarg)
        if nested_id is not None:
            try:
                obj = self.model.objects.get(id=nested_id)
            except self.model.DoesNotExist:
                return False
        return self.decorated_instance.has_object_permission(request, view, obj)


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class OwnerIncludedLink(AccessibleChain):
    @login_required_link
    def handle(self, q=None):
        if q is None:
            q = Q()

        q |= Q(user=self.request.user)
        return super().handle(q)


def get_accessible_q(request, links):
    root = AccessibleChain(request=request)
    for l in links:
        root.add(l())
    return root.handle()


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