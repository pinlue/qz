from __future__ import annotations

from typing import TYPE_CHECKING

import deepl
from deepl import (
    AuthorizationException,
    QuotaExceededException,
    TooManyRequestsException,
    DeepLException,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    inline_serializer,
)
from rest_framework import viewsets, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from common.permissions import IsObjOwner, IsObjAdmin
from .models import DeepLApiKey
from .permissions import HasAcceptedDeepLApiKeyView
from .serializers import (
    DeepLApiKeySerializer,
    DeepLApiKeyCreateSerializer,
    TranslationSerializer,
    DeepLApiKeyUpdateSerializer,
)

if TYPE_CHECKING:
    from typing import Type
    from rest_framework.serializers import Serializer
    from rest_framework.permissions import BasePermission
    from rest_framework.request import Request


@extend_schema(tags=["deepl"])
class DeepLApiKeyViewSet(viewsets.ModelViewSet):
    queryset = DeepLApiKey.objects.all()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "create":
            return DeepLApiKeyCreateSerializer
        if self.action in {"update", "partial_update"}:
            return DeepLApiKeyUpdateSerializer
        return DeepLApiKeySerializer

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "list":
            return [permissions.IsAdminUser()]
        elif self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action in {"retrieve", "update", "partial_update", "destroy"}:
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
                    "translations": serializers.ListField(child=serializers.CharField())
                },
            ),
        ),
        502: OpenApiResponse(
            description="Translation failed",
            response=inline_serializer(name="EmptyResponse", fields={}),
        ),
    },
)
class DeepLTranslationsView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasAcceptedDeepLApiKeyView]

    def post(self, request: Request) -> Response:
        serializer = TranslationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        words = serializer.validated_data["words"]
        lang_to = serializer.validated_data["lang_to"]

        translator = deepl.Translator(request.user.deeplapikey.api_key)
        try:
            translations = [
                translator.translate_text(word, target_lang=lang_to.code).text
                for word in words
            ]
        except AuthorizationException:
            return Response(
                {"detail": "Invalid DeepL API ke"}, status=status.HTTP_401_UNAUTHORIZED
            )
        except QuotaExceededException:
            return Response(
                {"detail": "DeepL usage quota exceeded"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except TooManyRequestsException:
            return Response(
                {"detail": "Too many requests to DeepL API. Please retry later"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        except DeepLException:
            return Response(
                {"detail": "Translation service unavailable"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response({"translations": translations})
