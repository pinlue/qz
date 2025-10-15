import deepl
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    inline_serializer,
)
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsObjOwner, IsObjAdmin
from .models import DeepLApiKey
from .permissions import HasAcceptedDeepLApiKeyView
from .serializators import DeepLApiKeySerializer, DeepLApiKeyCreateSerializer, TranslationSerializer, \
    DeepLApiKeyUpdateSerializer


@extend_schema(tags=["deepl"])
class DeepLApiKeyViewSet(viewsets.ModelViewSet):
    queryset = DeepLApiKey.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return DeepLApiKeyCreateSerializer
        if self.action in {'update', 'partial_update'}:
            return DeepLApiKeyUpdateSerializer
        return DeepLApiKeySerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in {'retrieve', 'update', 'partial_update', 'destroy'}:
            return [(IsObjAdmin | IsObjOwner)()]
        return super().get_permissions()


@extend_schema(
    tags=["deepl"],
    request=TranslationSerializer,
    responses={
        200: OpenApiResponse(
            description="Successful translation",
            response=inline_serializer(
                name="TranslationsResponse",
                fields={
                    "translations": serializers.ListField(
                        child=serializers.CharField()
                    )
                },
            ),
        ),
        502: OpenApiResponse(
            description="Translation failed",
            response=inline_serializer(
                name="EmptyResponse",
                fields={}
            ),
        ),
    },
)
class DeepLTranslationsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasAcceptedDeepLApiKeyView]

    def post(self, request):
        serializer = TranslationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        words = serializer.validated_data['words']
        to_lang = serializer.validated_data['to_lang']

        translator = deepl.Translator(request.user.deeplapikey.api_key)
        try:
            translations = [
                translator.translate_text(word, target_lang=to_lang).text
                for word in words
            ]
        except Exception:
            return Response(status=status.HTTP_502_BAD_GATEWAY)
        return Response({'translations': translations})
