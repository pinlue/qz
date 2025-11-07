from rest_framework import permissions
from rest_framework.permissions import BasePermission


class InteractionsPermsMixin:
    def get_permissions(self) -> list[BasePermission]:
        if self.action in {"pins", "saves"}:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
