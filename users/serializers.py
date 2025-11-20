from rest_framework import serializers
from taggit.serializers import TagListSerializerField

from folders.models import Folder
from modules.models import Module
from users.models import User


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar"]


class UserFolderListSerializer(serializers.ModelSerializer):
    modules_count = serializers.IntegerField(read_only=True)

    saved = serializers.BooleanField()
    pinned = serializers.BooleanField()

    class Meta:
        model = Folder
        fields = ["id", "user", "name", "color", "modules_count", "saved", "pinned"]


class UserModuleListSerializer(serializers.ModelSerializer):
    cards_count = serializers.IntegerField(read_only=True)
    tags = TagListSerializerField()

    saved = serializers.BooleanField()
    pinned = serializers.BooleanField()

    user_perm = serializers.CharField()
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
            "user",
            "name",
            "tags",
            "cards_count",
            "saved",
            "pinned",
            "user_perm",
            "avg_rate"
        ]


class UserPublicDetailSerializer(serializers.ModelSerializer):
    folders = UserFolderListSerializer(many=True, read_only=True)
    modules = UserModuleListSerializer(many=True, read_only=True)

    public_modules_count = serializers.IntegerField(read_only=True)
    public_folders_count = serializers.IntegerField(read_only=True)
    total_cards_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "avatar",
            "bio",
            "date_joined",
            "folders",
            "modules",
            "public_modules_count",
            "public_folders_count",
            "total_cards_count",
        ]


class UserPrivateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "avatar", "first_name", "last_name", "bio", "email", "date_joined"]
        read_only_fields = ["id", "email", "date_joined"]
