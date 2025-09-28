import deepl
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import comb_perm, IsOwner
from .models import DeepLApiKey
from .permissions import HasAcceptedDeepLApiKeyPermission
from .serializators import DeepLApiKeySerializer, DeepLApiKeyCreateSerializer, TranslationSerializer


class DeepLApiKeyViewSet(viewsets.ModelViewSet):
    queryset = DeepLApiKey.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return DeepLApiKeyCreateSerializer
        return DeepLApiKeySerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action in {'retrieve', 'update', 'partial_update', 'destroy'}:
            return [comb_perm(any,(
                permissions.IsAdminUser,
                IsOwner
            ))()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if self.action == 'list':
            return DeepLApiKey.objects.all()
        return DeepLApiKey.objects.filter(user=user)


class DeepLTranslationsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasAcceptedDeepLApiKeyPermission]

    @swagger_auto_schema(
        request_body=TranslationSerializer,
        responses={
            200: openapi.Response(
                description="Successful translation",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "translations": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "translations": ["translated_word1", "translated_word2"]
                    }
                }
            ),
            502: openapi.Response(
                description="Translation failed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING)
                    }
                ),
                examples={
                    "application/json": {"detail": "Translation failed."}
                }
            ),
        }
    )
    def post(self, request):
        serializer = TranslationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        words = serializer.validated_data['words']
        target_lang = serializer.validated_data['target_lang']

        translator = deepl.Translator(request.user.deeplapikey.api_key)
        try:
            translations = [
                translator.translate_text(word, target_lang=target_lang).text
                for word in words
            ]
        except Exception:
            return Response({'detail': 'Translation failed.'}, status=status.HTTP_502_BAD_GATEWAY)
        return Response({'translations': translations})