from rest_framework import permissions

from integration.models import DeepLApiKey


class HasAcceptedDeepLApiKeyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_authenticated and request.user.deeplapikey.status == "ACCEPTED"
        except DeepLApiKey.DoesNotExist:
            return False