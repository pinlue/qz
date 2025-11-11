from rest_framework import serializers

from languages.serializers import LanguageShortSerializer
from modules.models import Module
from topics.serializers import TopicSerializer
from users.serializers import UserPublicSerializer
from .models import Folder


class FolderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ["id", "user", "name", "color"]
        read_only_fields = ["id", "user"]


class FolderListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    modules_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Folder
        fields = ["id", "user", "name", "color", "modules_count"]


class FolderModuleListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageShortSerializer(read_only=True)
    lang_to = LanguageShortSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    cards_count = serializers.IntegerField(read_only=True)

    saved = serializers.BooleanField()
    pinned = serializers.BooleanField()

    user_perm = serializers.CharField()

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
            "pinned",
            "user_perm",
        ]


class FolderDetailSerializer(serializers.ModelSerializer):
    modules_count = serializers.IntegerField(read_only=True)
    modules = FolderModuleListSerializer(many=True, read_only=True)

    saved = serializers.BooleanField()
    pinned = serializers.BooleanField()

    class Meta:
        model = Folder
        fields = [
            "id",
            "user",
            "name",
            "color",
            "modules_count",
            "modules",
            "saved",
            "pinned",
        ]
