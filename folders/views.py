from django.db.models import Count
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from common.permissions import comb_perm, IsOwner
from folders.models import Folder
from folders.serializators import FolderListSerializer, FolderDetailSerializer, FolderCreateUpdateSerializer
from modules.models import Module
from modules.serializators import ModuleIdSerializer


class FolderViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        base_qs = Folder.objects.select_related('user')
        if self.action == 'list':
            return base_qs.annotate(modules_count=Count('modules'))
        elif self.action == 'retrieve':
            return base_qs.annotate(modules_count=Count('modules')).prefetch_related('modules')
        return base_qs

    def get_serializer_class(self):
        if self.action == 'list':
            return FolderListSerializer
        elif self.action == 'retrieve':
            return FolderDetailSerializer
        elif self.action in {'create', 'update', 'partial_update'}:
            return FolderCreateUpdateSerializer
        return FolderListSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [comb_perm(any, (
                permissions.IsAdminUser,
                IsOwner,
            ))()]
        elif self.action in {'list', 'retrieve'}:
            return [permissions.AllowAny()]
        else:
            return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        methods=['post', 'delete'],
        manual_parameters=[
            openapi.Parameter(
                'module_id',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=no_body,
        responses={
            201: openapi.Response("Module added to folder"),
            204: openapi.Response("Module removed from folder"),
            400: openapi.Response("Bad request"),
            404: openapi.Response("Module not found"),
            405: openapi.Response("Method not allowed"),
        }
    )
    @action(detail=True, methods=['post', 'delete'], url_path='modules/(?P<module_id>[^/.]+)',
            permission_classes=[comb_perm(any, (permissions.IsAdminUser, IsOwner)),])
    def manage_module(self, request, pk=None, module_id=None):
        folder = self.get_object()
        serializer = ModuleIdSerializer(data={'id': module_id})
        serializer.is_valid(raise_exception=True)
        module = Module.objects.get(id=serializer.validated_data['id'])

        if request.method == 'POST':
            folder.modules.add(module)
            return Response({'status': 'module added'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            folder.modules.remove(module)
            return Response({'status': 'module removed'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
