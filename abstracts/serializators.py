from rest_framework import serializers

from abstracts.models import Visible


class TagsSerializer(serializers.Serializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        allow_empty=False
    )


class VisibleSerializer(serializers.Serializer):
    visible = serializers.ChoiceField(choices=Visible.Status.choices)
