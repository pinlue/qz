from rest_framework import serializers

from cards.models import Card


class UniqueCardValidatorMixin:
    def validate(self, attrs):
        module_pk = self.context["view"].kwargs.get("module_pk")

        if not module_pk:
            raise serializers.ValidationError('Missing "module_pk" parameter')

        exists = Card.objects.filter(
            module_id=module_pk,
            original=attrs.get("original"),
            translation=attrs.get("translation"),
        ).exists()

        if exists:
            raise serializers.ValidationError(
                "Card with this original and translation already exists in this module."
            )

        return attrs


class CardSerializer(UniqueCardValidatorMixin, serializers.ModelSerializer):
    saved = serializers.BooleanField(read_only=True)

    class Meta:
        model = Card
        fields = ["id", "original", "translation", "module", "saved"]
        read_only_fields = ["id", "module", "saved"]


class CardShortSerializer(serializers.ModelSerializer):
    saved = serializers.BooleanField()

    learned_status = serializers.CharField()

    class Meta:
        model = Card
        fields = ["id", "original", "translation", "saved", "learned_status"]


class CardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ["original", "translation"]
