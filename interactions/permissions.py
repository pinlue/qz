from rest_framework import permissions

from abstracts.permissions import IsPublic
from common.permissions import comb_perm, IsOwner


class InteractionsPermsMixin:
    def get_permissions(self):
        if self.action in {'pins', 'saves'}:
            return [comb_perm(any,(
                comb_perm(all,(
                    permissions.IsAuthenticated,
                    IsPublic,
                ))(),
                permissions.IsAdminUser,
                IsOwner,
            ))()]
        return super().get_permissions()