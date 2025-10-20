from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .clients import CustomOAuth2Client
from .serializers import EmailChangeSerializer, EmailVerifySerializer
from allauth.account.models import EmailAddress

from .tasks import send_verification_email, schedule_email_deletion


@extend_schema_view(
    post=extend_schema(
        request=EmailChangeSerializer,
        responses={
            200: {
                "description": "Verification email sent",
                "content": {"application/json": {"example": {"detail": "verification email sent"}}},
            },
            400: {"description": "Invalid input"},
        },
    )
)
class EmailChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = EmailChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data['new_email']
        user = request.user

        email_obj, created = EmailAddress.objects.get_or_create(
            user=user, email=new_email, defaults={'verified': False, 'primary': False}
        )
        if not created and not email_obj.verified:
            return Response({'status': 'ok'})

        schedule_email_deletion(email_obj.user_id, email_obj.email)
        send_verification_email.delay(email_obj.user_id, email_obj.email)

        return Response({'detail': 'verification email sent'}, status=status.HTTP_200_OK)


@extend_schema_view(
    post=extend_schema(
        request=EmailVerifySerializer,
        responses={
            200: {
                "description": "Email verified",
                "content": {"application/json": {"example": {
                    "status": "ok",
                    "email": "user@example.com",
                    "primary": True,
                    "verified": True
                }}}},
            400: {"description": "Invalid input"},
        },
    )
)
class EmailVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = EmailVerifySerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        email_address = serializer.save()

        return Response({
            "status": "ok",
            "email": email_address.email,
            "primary": email_address.primary,
            "verified": email_address.verified,
        }, status=status.HTTP_200_OK)


class GitHubLoginView(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/api/v1/auth/login/github/callback/"
    client_class = CustomOAuth2Client


class GoogleLoginView(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/api/v1/auth/login/google/callback/"
    client_class = CustomOAuth2Client
