from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import QuerySet

from abstracts.permissions import PublicIncludedLink
from common.permissions import get_accessible_q, OwnerIncludedLink
from folders.repository import FolderRepository
from modules.service import ModuleService

if TYPE_CHECKING:
    from rest_framework.request import Request
    from django.http import HttpRequest
    from folders.models import Folder


class FolderService:
    LIST_ACTION_CHAIN_LINKS = [
        PublicIncludedLink,
        OwnerIncludedLink,
    ]

    def __init__(
        self,
        request: Request | HttpRequest,
        action: str,
    ) -> None:
        self.request = request
        self.action = action

    def get_queryset(self) -> QuerySet[Folder]:
        base_qs = FolderRepository.base_qs()

        if self.action not in {"list", "retrieve"}:
            return base_qs

        modules_q = get_accessible_q(
            self.request, ModuleService.LIST_ACTION_CHAIN_LINKS
        )
        qs = FolderRepository.with_modules_count(base_qs, modules_q)
        user = self.request.user

        if self.action == "list":
            return FolderRepository.accessible_for_user(
                qs, self.request, self.LIST_ACTION_CHAIN_LINKS
            )

        if self.action == "retrieve":
            return FolderRepository.with_modules_prefetched(qs, user, modules_q)

        return base_qs
