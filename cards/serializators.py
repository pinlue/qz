from rest_framework import serializers

from cards.models import Card


class CardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["id", "original", "translation", "module"]
        read_only_fields = ["id", "module"]


class CardShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["id", "original", "translation"]


class CardInputSerializer(serializers.Serializer):
    original = serializers.CharField(max_length=100)
    translation = serializers.CharField(max_length=100)
