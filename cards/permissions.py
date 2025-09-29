from rest_framework import permissions
from modules.models import Module


class IsModuleOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        module_pk = view.kwargs.get('module_pk')
        if not module_pk or not request.user.is_authenticated:
            return False
        try:
            module = Module.objects.get(pk=module_pk)
        except Module.DoesNotExist:
            return False
        return module.user == request.user