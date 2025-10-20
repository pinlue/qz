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

    class Meta:
        model = Folder
        fields = ['id', 'user', 'name', 'color', 'modules_count']


class UserModuleListSerializer(serializers.ModelSerializer):
    cards_count = serializers.IntegerField(read_only=True)
    tags = TagListSerializerField()

    class Meta:
        model = Module
        fields = ["id", "user", "name", "tags", "cards_count"]


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
        fields = ["id", "username", "avatar", "first_name", "last_name", "bio", "email"]
        read_only_fields = ["id", "email"]
