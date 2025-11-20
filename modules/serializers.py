from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import transaction
from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from cards.serializers import (
    CardShortSerializer,
    CardCreateSerializer,
)
from languages.serializers import LanguageShortSerializer, LanguageSerializer
from modules.models import Module
from topics.models import Topic
from topics.serializers import TopicSerializer
from users.serializers import UserPublicSerializer

if TYPE_CHECKING:
    from typing import Any


class ModuleListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageShortSerializer(read_only=True)
    lang_to = LanguageShortSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    cards_count = serializers.IntegerField(read_only=True)
    avg_rate = serializers.DecimalField(
        read_only=True,
        max_digits=3,
        decimal_places=1,
        coerce_to_string=False
    )

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
            "avg_rate",
        ]


class ModulePatchSerializer(serializers.ModelSerializer):
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
        ]
        read_only_fields = ["user"]


class ModuleCreatePutSerializer(serializers.ModelSerializer):
    cards = CardCreateSerializer(many=True, write_only=True, required=False)

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

    def create(self, validated_data: dict[str, Any]) -> Module:
        cards_data = validated_data.pop("cards", [])
        unique_cards = {(card["original"], card["translation"]) for card in cards_data}

        with transaction.atomic():
            module = Module.objects.create(**validated_data)

            if unique_cards:
                from cards.models import Card

                Card.objects.bulk_create(
                    [
                        Card(original=o, translation=t, module=module)
                        for o, t in unique_cards
                    ]
                )

            return module


class ModuleDetailSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageSerializer(read_only=True)
    lang_to = LanguageSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    tags = TagListSerializerField()

    cards = CardShortSerializer(many=True, read_only=True)
    cards_count = serializers.IntegerField(read_only=True)

    saved = serializers.BooleanField()
    pinned = serializers.BooleanField()

    user_rate = serializers.CharField()
    user_perm = serializers.CharField()

    class Meta:
        model = Module
        fields = [
            "id",
            "name",
            "description",
            "user",
            "tags",
            "lang_from",
            "lang_to",
            "topic",
            "cards",
            "cards_count",
            "saved",
            "pinned",
            "user_rate",
            "user_perm",
        ]


class ModuleMergeSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())
    modules = serializers.ListField(
        child=serializers.IntegerField(), min_length=2, max_length=5
    )

    def validate_modules(self, module_ids: list[int]) -> list[Module]:
        modules = list(Module.objects.filter(id__in=module_ids))
        if len(modules) != len(module_ids):
            raise serializers.ValidationError("Some modules were not found")

        lang_from_set = {m.lang_from_id for m in modules}
        lang_to_set = {m.lang_to_id for m in modules}
        if len(lang_from_set) > 1 or len(lang_to_set) > 1:
            raise serializers.ValidationError(
                "All modules must have the same languages"
            )

        return modules
