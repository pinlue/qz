from rest_framework import serializers

from modules.serializers import ModuleListSerializer
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

    saved = serializers.BooleanField()
    pinned = serializers.BooleanField()

    class Meta:
        model = Folder
        fields = ["id", "user", "name", "color", "modules_count", "saved", "pinned"]


class FolderDetailSerializer(serializers.ModelSerializer):
    modules_count = serializers.IntegerField(read_only=True)
    modules = ModuleListSerializer(many=True, read_only=True)

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
