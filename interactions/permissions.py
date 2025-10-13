from rest_framework import permissions


class InteractionsPermsMixin:
    def get_permissions(self):
        if self.action in {'pins', 'saves'}:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()