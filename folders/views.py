from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q, Prefetch
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema, no_body
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from abstracts.permissions import IsPublic
from abstracts.views import VisibleMixin
from common.permissions import comb_perm, IsOwner
from folders.models import Folder
from folders.permissions import NestedModuleIsPublic, NestedModuleIsViewer, NestedModuleIsEditor, NestedModuleIsOwner
from folders.serializators import FolderListSerializer, FolderDetailSerializer, FolderCreateUpdateSerializer
from generic_status.models import Perm
from interactions.views import PinMixin, SaveMixin
from modules.models import Module


class FolderViewSet(PinMixin, SaveMixin, VisibleMixin, viewsets.ModelViewSet):
    def get_queryset(self):
        base_qs = Folder.objects.select_related("user")
        module_ct = ContentType.objects.get_for_model(Module)

        if self.request.user.is_authenticated:
            user = self.request.user
            modules_filter = (
                    Q(visible="public")
                    | Q(user=user)
                    | Q(
                id__in=Perm.objects.filter(
                    content_type=module_ct,
                    user=user,
                    perm__in=["editor", "viewer"]
                ).values("object_id")
            )
            )
        else:
            modules_filter = Q(visible="public")

        if self.action in {"list", "retrieve"}:
            qs = base_qs.annotate(
                modules_count=Count(
                    "modules",
                    filter=Q(modules__in=Module.objects.filter(modules_filter)),
                    distinct=True,
                )
            )
            if self.action == "list":
                return qs.filter(visible="public")
            if self.action == "retrieve":
                return qs.prefetch_related(
                    Prefetch(
                        "modules",
                        queryset=Module.objects.filter(modules_filter)
                        .select_related("user", "topic", "lang_from", "lang_to")
                        )
                    )
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
        elif self.action == 'list':
            return [permissions.AllowAny()]
        elif self.action == 'retrieve':
            return [comb_perm(any, (
                permissions.IsAdminUser,
                IsOwner,
                IsPublic,
            ))()]
        else:
            return super().get_permissions()

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
            permission_classes=[
                comb_perm(any, (
                    IsAdminUser,
                    comb_perm(all, (
                        IsOwner,
                        comb_perm(any, (
                            NestedModuleIsPublic,
                            NestedModuleIsViewer,
                            NestedModuleIsEditor,
                            NestedModuleIsOwner
                        ))
                    ))
                ))
            ])
    def manage_module(self, request, pk=None, module_id=None):
        folder = self.get_object()
        module = get_object_or_404(Module, id=module_id)

        if request.method == 'POST':
            folder.modules.add(module)
            return Response({'status': 'module added'}, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            folder.modules.remove(module)
            return Response({'status': 'module removed'}, status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
