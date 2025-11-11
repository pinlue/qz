from __future__ import annotations

from typing import TYPE_CHECKING

from users.repository import UserRepository

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from rest_framework.request import Request
    from users.models import User
    from django.http import HttpRequest


class UserService:
    def __init__(self, request: Request | HttpRequest, action: str) -> None:
        self.request = request
        self.action = action

    def get_queryset(self) -> QuerySet[User]:
        qs = UserRepository.base_qs()

        if self.action == "list":
            return qs

        if self.action == "retrieve":
            user = self.request.user
            qs = UserRepository.with_prefetched_related(qs, self.request, user)
            qs = UserRepository.with_public_counts(qs)
            return qs

        return qs
