from rest_framework import serializers

from languages.serializators import LanguageShortSerializer, LanguageSerializer
from modules.models import Module
from topics.serializators import TopicSerializer
from users.serializators import UserPublicSerializer


class ModuleListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageShortSerializer(read_only=True)
    lang_to = LanguageShortSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'user', 'lang_from', 'lang_to', 'topic']


class ModuleCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['name', 'description', 'user', 'topic', 'lang_from', 'lang_to']
        read_only_fields = ['user']


class ModuleDetailSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageSerializer(read_only=True)
    lang_to = LanguageSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'user', 'lang_from', 'lang_to', 'topic']


class ModuleIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id']