from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializators import EmailChangeSerializer, EmailVerifySerializer
from allauth.account.models import EmailAddress

from .tasks import send_verification_email, schedule_email_deletion


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

        schedule_email_deletion(email_obj.user_id, email_obj.email, delay_days=3)
        send_verification_email.delay(email_obj.user_id, email_obj.email)

        return Response({'detail': 'verification email sent'}, status=status.HTTP_200_OK)


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
