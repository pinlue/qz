from rest_framework import serializers

from generic_status.models import Learn, Rate, Perm


class LearnSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Learn.Status.choices)


class RateSerializer(serializers.Serializer):
    rating = serializers.ChoiceField(choices=Rate.Status.choices)


class PermSerializer(serializers.Serializer):
    perm = serializers.ChoiceField(choices=Perm.Status.choices)