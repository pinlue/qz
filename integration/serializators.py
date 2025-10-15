from django.core.validators import RegexValidator
from rest_framework import serializers
from languages.models import Language
from .models import DeepLApiKey
import deepl


class DeepLApiKeyCreateSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True)

    class Meta:
        model = DeepLApiKey
        fields = ['api_key']

    def validate(self, attrs):
        user = self.context.get('request').user
        if DeepLApiKey.objects.filter(user=user).exists():
            raise serializers.ValidationError("Key already exists for this user.")
        return attrs

    def create(self, validated_data):
        user = self.context.get('request').user
        api_key = validated_data['api_key']
        instance = DeepLApiKey(user=user)
        instance.api_key = api_key
        instance.save()
        return instance


class DeepLApiKeyUpdateSerializer(serializers.ModelSerializer):
    api_key = serializers.CharField(write_only=True)

    class Meta:
        model = DeepLApiKey
        fields = ['api_key']

    def update(self, instance, validated_data):
        instance.api_key = validated_data.get('api_key', instance.api_key)
        instance.status = "PENDING"
        instance.save()
        return instance


class DeepLApiKeySerializer(serializers.ModelSerializer):
    remaining_characters = serializers.SerializerMethodField()

    class Meta:
        model = DeepLApiKey
        fields = ['id', 'status', 'user', 'remaining_characters']

    def get_remaining_characters(self, obj) -> int | None:
        try:
            api_key = obj.api_key
            translator = deepl.Translator(api_key)
            usage = translator.get_usage()
            if usage.character.limit is not None and usage.character.count is not None:
                return usage.character.limit - usage.character.count
        except Exception:
            pass
        return None


class TranslationSerializer(serializers.Serializer):
    words = serializers.ListField(
        child=serializers.CharField(), min_length=1
    )
    to_lang = serializers.CharField(validators=[RegexValidator(regex=r'^[A-Z]{2,3}$')])

    def validate_to_lang(self, value):
        if not Language.objects.filter(code=value).exists():
            raise serializers.ValidationError("Language not supported.")
        return value