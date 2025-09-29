from rest_framework import serializers

from cards.serializators import CardShortSerializer, CardInputSerializer
from languages.serializators import LanguageShortSerializer, LanguageSerializer
from modules.models import Module
from topics.serializators import TopicSerializer
from users.serializators import UserPublicSerializer


class ModuleListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageShortSerializer(read_only=True)
    lang_to = LanguageShortSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    cards_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'user', 'lang_from', 'lang_to', 'topic', 'cards_count']


class ModuleCreateUpdateSerializer(serializers.ModelSerializer):
    cards = CardInputSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Module
        fields = ['name', 'description', 'user', 'topic', 'lang_from', 'lang_to', 'cards']
        read_only_fields = ['user']

    def create(self, validated_data):
        cards_data = validated_data.pop('cards', [])
        module = Module.objects.create(**validated_data)
        if cards_data:
            from cards.models import Card
            Card.objects.bulk_create([
                Card(original=card['original'], translation=card['translation'], module=module)
                for card in cards_data
            ])
        return module


class ModuleDetailSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)
    lang_from = LanguageSerializer(read_only=True)
    lang_to = LanguageSerializer(read_only=True)
    topic = TopicSerializer(read_only=True)

    cards = CardShortSerializer(many=True, read_only=True)
    cards_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Module
        fields = ['id', 'name', 'description', 'user', 'lang_from', 'lang_to', 'topic', 'cards_count', 'cards_count']


class ModuleIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id']