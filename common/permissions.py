from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any, Type, TypeVar, Callable

from rest_framework.permissions import BasePermission
from django.db.models import Q
from common.access_chain import AccessibleChain
from common.decorators import login_required_link

if TYPE_CHECKING:
    from django.db.models import Model
    from rest_framework.request import Request
    from rest_framework.views import APIView
    from django.http import HttpRequest


T = TypeVar("T", bound=BasePermission)


class RelatedObjPermissionProxy:
    def __init__(
        self,
        decorated: Callable[..., T],
        model: Type[Model],
        lookup_url_kwarg: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.decorated_instance: T = decorated(*args, **kwargs)
        self.model = model
        self.lookup_url_kwarg = lookup_url_kwarg

    def has_object_permission(
        self, request: Request, view: APIView, obj: Model
    ) -> bool:
        nested_id = view.kwargs.get(self.lookup_url_kwarg)
        if nested_id is not None:
            try:
                obj = self.model.objects.get(id=nested_id)
            except self.model.DoesNotExist:
                return False
        return self.decorated_instance.has_object_permission(request, view, obj)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.decorated_instance, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("decorated_instance", "model", "lookup_url_kwarg"):
            object.__setattr__(self, name, value)
        else:
            setattr(self.decorated_instance, name, value)

    def __delattr__(self, name: str) -> None:
        if name in ("decorated_instance", "model", "lookup_url_kwarg"):
            object.__delattr__(self, name)
        else:
            delattr(self.decorated_instance, name)


def partial_cls(base: Any, *args: Any, **kwargs: Any) -> Any:
    class Adapter(base):
        def __init__(self):
            super().__init__(*args, **kwargs)

    return Adapter


class IsObjOwner(BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        return obj.user == request.user


class IsObjAdmin(BasePermission):
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        return bool(request.user and request.user.is_staff)


class OwnerIncludedLink(AccessibleChain):
    @login_required_link
    def handle(self, q: Optional[Q] = None) -> Q:
        if q is None:
            q = Q()

        q |= Q(user=self.request.user)
        return super().handle(q)


def get_accessible_q(request: Request | HttpRequest, links: list[Type[AccessibleChain]]) -> Q:
    root = AccessibleChain(request)
    for l in links:
        root.add(l())
    return root.handle()
