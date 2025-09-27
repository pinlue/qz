from rest_framework import serializers
from .models import Folder


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'user', 'name', 'color']
        read_only_fields = ['id', 'user']