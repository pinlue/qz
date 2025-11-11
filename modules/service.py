from __future__ import annotations

from typing import TYPE_CHECKING

from abstracts.permissions import PublicIncludedLink
from common.permissions import OwnerIncludedLink, partial_cls
from generic_status.permissions import PermissionIncludedLink
from modules.models import Module
from modules.repository import ModuleRepository

if TYPE_CHECKING:
    from common.access_chain import AccessibleChain
    from rest_framework.request import Request
    from typing import Type
    from django.http import HttpRequest


class ModuleService:
    LIST_ACTION_CHAIN_LINKS: list[Type[AccessibleChain]] = [
        PublicIncludedLink,
        OwnerIncludedLink,
        partial_cls(PermissionIncludedLink, model=Module, perms=["editor", "viewer"]),
    ]

    def __init__(self, request: Request | HttpRequest, action: str):
        self.request = request
        self.action = action

    def get_queryset(self):
        qs = ModuleRepository.base_qs()

        if self.action in {"list", "retrieve"}:
            user = self.request.user

            if self.action == "retrieve":
                qs = ModuleRepository.with_cards_and_annotations(qs, user)

            elif self.action == "list":
                qs = ModuleRepository.accessible_for_user(
                    qs, self.request, self.LIST_ACTION_CHAIN_LINKS
                )

        return qs
