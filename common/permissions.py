from django.db.models import Q
from rest_framework.permissions import BasePermission

from common.access_chain import AccessibleChain
from common.decorators import login_required_link


class RelatedObjPermissionProxy:
    def __init__(self, decorated, model, lookup_url_kwarg, *args, **kwargs):
        self.decorated_instance = decorated(*args, **kwargs)
        self.model = model
        self.lookup_url_kwarg = lookup_url_kwarg

    def has_object_permission(self, request, view, obj):
        nested_id = view.kwargs.get(self.lookup_url_kwarg)
        if nested_id is not None:
            try:
                obj = self.model.objects.get(id=nested_id)
            except self.model.DoesNotExist:
                return False
        return self.decorated_instance.has_object_permission(request, view, obj)

    def __getattr__(self, name):
        return getattr(self.decorated_instance, name)

    def __setattr__(self, name, value):
        if name in ('decorated_instance', 'model', 'lookup_url_kwarg'):
            object.__setattr__(self, name, value)
        else:
            setattr(self.decorated_instance, name, value)

    def __delattr__(self, name):
        if name in ('decorated_instance', 'model', 'lookup_url_kwarg'):
            object.__delattr__(self, name)
        else:
            delattr(self.decorated_instance, name)


def partial_cls(base, *args, **kwargs):
    class Adapter(base):
        def __init__(self):
            super().__init__(*args, **kwargs)
    return Adapter


class IsObjOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsObjAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff)


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