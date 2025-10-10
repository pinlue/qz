from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializators import EmailChangeSerializer, EmailVerifySerializer
from allauth.account.models import EmailAddress

from .tasks import send_verification_email, schedule_email_deletion


class EmailChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=EmailChangeSerializer,
        responses={
            200: openapi.Response(
                description='Verification email sent',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'detail': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response('Invalid input'),
        },
        operation_description="Change user email and send verification email.",
        tags=["auth"]
    )
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



class EmailVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        request_body=EmailVerifySerializer,
        responses={
            200: openapi.Response(
                description='Email verified',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'primary': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    }
                )
            ),
            400: openapi.Response('Invalid input'),
        },
        operation_description="Verify user email.",
        tags=["auth"]
    )
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
