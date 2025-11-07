from __future__ import annotations
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from rest_framework.permissions import BasePermission

from common.access_chain import AccessibleChain
from common.decorators import login_required_link
from generic_status.models import Perm

if TYPE_CHECKING:
    from typing import Any, Optional
    from rest_framework.request import Request
    from rest_framework.views import APIView


class HasObjRoles(BasePermission):
    def __init__(self, roles: list[str] | list[Perm.Status]) -> None:
        self.roles = roles

    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        ct = ContentType.objects.get_for_model(obj.__class__)
        return Perm.objects.filter(
            user=request.user, object_id=obj.id, perm__in=self.roles, content_type=ct
        ).exists()


class PermissionIncludedLink(AccessibleChain):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.model = kwargs.pop("model")
        self.perms = kwargs.pop("perms")
        super().__init__(*args, **kwargs)

    @login_required_link
    def handle(self, q: Optional[Q] = None) -> Q:
        if q is None:
            q = Q()

        q |= Q(
            id__in=Perm.objects.filter(
                content_type=ContentType.objects.get_for_model(self.model),
                user=self.request.user,
                perm__in=self.perms,
            ).values("object_id")
        )
        return super().handle(q)
