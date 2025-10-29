from rest_framework import serializers

from cards.serializers import CardShortSerializer, CardInputSerializer
from languages.serializers import LanguageShortSerializer, LanguageSerializer
from modules.models import Module
from topics.models import Topic
from topics.serializers import TopicSerializer
from users.serializers import UserPublicSerializer


class ModuleListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageShortSerializer(read_only=True)
    lang_to = LanguageShortSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    cards_count = serializers.IntegerField(read_only=True)

    saved = serializers.BooleanField()
    pinned = serializers.BooleanField()

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "description",
            "user",
            "lang_from",
            "lang_to",
            "topic",
            "cards_count",
            "saved",
            "pinned"
        ]


class ModuleCreateUpdateSerializer(serializers.ModelSerializer):
    cards = CardInputSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "description",
            "user",
            "topic",
            "lang_from",
            "lang_to",
            "cards",
        ]
        read_only_fields = ["user"]

    def create(self, validated_data):
        cards_data = validated_data.pop("cards", [])
        module = Module.objects.create(**validated_data)
        if cards_data:
            from cards.models import Card

            Card.objects.bulk_create(
                [
                    Card(
                        original=card["original"],
                        translation=card["translation"],
                        module=module,
                    )
                    for card in cards_data
                ]
            )
        return module


class ModuleDetailSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageSerializer(read_only=True)
    lang_to = LanguageSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    cards = CardShortSerializer(many=True, read_only=True)
    cards_count = serializers.IntegerField(read_only=True)

    saved = serializers.BooleanField()
    pinned = serializers.BooleanField()

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "description",
            "user",
            "lang_from",
            "lang_to",
            "topic",
            "cards",
            "cards_count",
            "saved",
            "pinned"
        ]


class ModuleMergeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())
    modules = serializers.ListField(
        child=serializers.IntegerField(), min_length=2, max_length=5
    )

    def validate_modules(self, module_ids):
        modules = list(Module.objects.filter(id__in=module_ids))
        if len(modules) != len(module_ids):
            raise serializers.ValidationError("Some modules were not found.")

        lang_from_set = {m.lang_from_id for m in modules}
        lang_to_set = {m.lang_to_id for m in modules}
        if len(lang_from_set) > 1 or len(lang_to_set) > 1:
            raise serializers.ValidationError(
                "All modules must have the same languages."
            )

        return modules
