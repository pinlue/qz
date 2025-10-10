from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework.permissions import BasePermission

from common.access_chain import AccessibleChain
from common.decorators import login_required_link
from generic_status.models import Perm


class BaseRolePermission(BasePermission):
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


class PermissionIncludedLink(AccessibleChain):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        self.perms = kwargs.pop('perms')
        super().__init__(*args, **kwargs)

    @login_required_link
    def handle(self, q=None):
        if q is None:
            q = Q()

        q |= Q(
                id__in=Perm.objects.filter(
                    content_type=ContentType.objects.get_for_model(self.model),
                    user=self.request.user,
                    perm__in=self.perms
                ).values("object_id")
            )
        return super().handle(q)


