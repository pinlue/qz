from rest_framework import serializers
from allauth.account.models import EmailAddress, EmailConfirmationHMAC, EmailConfirmation


class EmailChangeSerializer(serializers.Serializer):
    new_email = serializers.EmailField()

    def validate_new_email(self, value):
        user = self.context.get('request').user
        if EmailAddress.objects.filter(email=value, verified=True).exclude(user=user).exists() or value == user.email:
            raise serializers.ValidationError('Email already in use')
        return value


class EmailVerifySerializer(serializers.Serializer):
    key = serializers.CharField()

    def validate_key(self, key):
        confirmation = EmailConfirmationHMAC.from_key(key) or EmailConfirmation.objects.filter(key=key).first()
        if not confirmation:
            raise serializers.ValidationError("Invalid verification key")
        return confirmation

    def save(self):
        request = self.context.get('request')
        confirmation = self.validated_data["key"]
        email_address = confirmation.confirm(request)
        return email_address