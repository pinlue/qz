from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import Q
from rest_framework.permissions import BasePermission

from abstracts.models import Visible
from common.access_chain import AccessibleChain

if TYPE_CHECKING:
    from typing import Optional
    from rest_framework.request import Request
    from rest_framework.views import APIView


class IsObjPublic(BasePermission):
    def has_object_permission(
        self,
        request: Request,
        view: APIView,
        obj: Visible,
    ) -> bool:
        return obj.visible == Visible.Status.PUBLIC


class PublicIncludedLink(AccessibleChain):
    def handle(self, q: Optional[Q] = None) -> Q:
        if q is None:
            q = Q()

        q |= Q(visible=Visible.Status.PUBLIC)
        return super().handle(q)
