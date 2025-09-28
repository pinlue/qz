from rest_framework import serializers

from modules.serializators import ModuleListSerializer
from .models import Folder


class FolderCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'user', 'name', 'color']
        read_only_fields = ['id', 'user']


class FolderListSerializer(serializers.ModelSerializer):
    modules_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'user', 'name', 'color', 'modules_count']


class FolderDetailSerializer(serializers.ModelSerializer):
    modules_count = serializers.IntegerField(read_only=True)
    modules = ModuleListSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'user', 'name', 'color', 'modules_count', 'modules']