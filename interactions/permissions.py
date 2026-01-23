from rest_framework import permissions
from rest_framework.permissions import BasePermission

from common.permissions import IsObjAdmin, IsObjOwner


class InteractionsPermsMixin:
    def get_permissions(self) -> list[BasePermission]:
        if self.action in {"pins", "saves"}:
            return [permissions.IsAuthenticated()]
        if self.action in {"user_saves_list", "user_pins_list"}:
            return [permissions.IsAuthenticated(), (IsObjAdmin | IsObjOwner)()]
        return super().get_permissions()
