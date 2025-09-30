from rest_framework import serializers

from abstracts.models import Visibles


class TagsSerializer(serializers.Serializer):
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        allow_empty=False
    )


class VisibleSerializer(serializers.Serializer):
    visible = serializers.ChoiceField(choices=Visibles.Status.choices)
