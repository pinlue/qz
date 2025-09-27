from rest_framework import viewsets, permissions

from common.permissions import comb_perm, IsOwner
from folders.models import Folder
from folders.serializators import FolderSerializer


class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [comb_perm(any, (
                permissions.IsAdminUser,
                IsOwner,
            ))]
        elif self.action in {'list', 'retrieve'}:
            return [permissions.AllowAny()]
        else:
            return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
