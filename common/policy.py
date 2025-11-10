from __future__ import annotations

from typing import TYPE_CHECKING

from common.exeptions import UnRegisteredPolicy

if TYPE_CHECKING:
    from typing import Type
    from rest_framework.permissions import BasePermission


class PolicyRegistry:
    def __init__(self) -> None:
        self._policies: dict[str, list[Type[BasePermission]]] = {}

    def register(self, action: str, permissions: list[Type[BasePermission]]) -> None:
        self._policies[action] = permissions

    def get(self, action: str) -> list[Type[BasePermission]]:
        if action not in self._policies:
            raise UnRegisteredPolicy("Policy doesn't exist")
        return self._policies[action]
