from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework import permissions


from integration.models import DeepLApiKey

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class HasAcceptedDeepLApiKeyView(permissions.BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        try:
            return (
                request.user.is_authenticated
                and request.user.deeplapikey.status == DeepLApiKey.Status.ACCEPTED
            )
        except DeepLApiKey.DoesNotExist:
            return False
