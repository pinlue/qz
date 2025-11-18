from __future__ import annotations

from typing import TYPE_CHECKING

from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from django.db import transaction
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .clients import CustomOAuth2Client
from .serializers import EmailChangeSerializer, EmailVerifySerializer
from .tasks import send_verification_email, schedule_email_deletion

if TYPE_CHECKING:
    from typing import Type
    from rest_framework.request import Request


@extend_schema_view(
    post=extend_schema(
        request=EmailChangeSerializer,
        responses={
            200: {
                "description": "Verification email sent",
                "content": {
                    "application/json": {
                        "example": {"detail": "verification email sent"}
                    }
                },
            },
            400: {"description": "Invalid input"},
        },
    )
)
class EmailChangeView(APIView):
    permission_classes: list[Type[permissions.BasePermission]] = [
        permissions.IsAuthenticated
    ]

    def post(self, request: Request) -> Response:
        serializer = EmailChangeSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data["new_email"]
        user = request.user

        with transaction.atomic():
            email_obj, created = EmailAddress.objects.select_for_update().get_or_create(
                user=user,
                email=new_email,
                defaults={"verified": False, "primary": False},
            )
            if not created and not email_obj.verified:
                return Response(
                    {"detail": "This email is already verified"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            schedule_email_deletion(email_obj.user_id, email_obj.email)
            send_verification_email.delay(email_obj.user_id, email_obj.email)

        return Response(
            {"detail": "verification email sent"}, status=status.HTTP_200_OK
        )


@extend_schema_view(
    post=extend_schema(
        request=EmailVerifySerializer,
        responses={
            200: {
                "description": "Email verified",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "ok",
                            "email": "user@example.com",
                            "primary": True,
                            "verified": True,
                        }
                    }
                },
            },
            400: {"description": "Invalid input"},
        },
    )
)
class EmailVerifyView(APIView):
    permission_classes: list[Type[permissions.BasePermission]] = [
        permissions.IsAuthenticated
    ]

    def post(self, request: Request) -> Response:
        serializer = EmailVerifySerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "email": request.user.email,
            },
            status=status.HTTP_200_OK,
        )


class GitHubLoginView(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = "http://localhost:3000/github/callback/"
    client_class = CustomOAuth2Client


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/google/callback/"
    client_class = CustomOAuth2Client
