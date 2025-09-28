from rest_framework import serializers

from users.models import User


#ToDo UserPrivateSerializer(and use it for dj_rest_auth.serializers.UserDetailsSerializer)
class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'avatar', 'bio']

