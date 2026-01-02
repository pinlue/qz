from rest_framework import serializers

from generic_status.models import Learn, Rate, Perm
from users.models import User
from users.serializers import UserPublicSerializer


class LearnSerializer(serializers.Serializer):
    learned = serializers.ChoiceField(choices=Learn.Status.choices)


class RateSerializer(serializers.Serializer):
    rate = serializers.ChoiceField(choices=Rate.Status.choices)


class PermSerializer(serializers.Serializer):
    perm = serializers.ChoiceField(choices=Perm.Status.choices)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())


class PermListSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Perm
        fields = ["id", "user", "perm"]
