from rest_framework import serializers

from cards.models import Card


class CardSerializer(serializers.ModelSerializer):
    saved = serializers.BooleanField()

    class Meta:
        model = Card
        fields = ["id", "original", "translation", "module", "saved"]
        read_only_fields = ["id", "module", "saved"]


class CardShortSerializer(serializers.ModelSerializer):
    saved = serializers.BooleanField()

    class Meta:
        model = Card
        fields = ["id", "original", "translation", "saved"]


class CardInputSerializer(serializers.Serializer):
    original = serializers.CharField(max_length=100)
    translation = serializers.CharField(max_length=100)
