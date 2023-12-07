from rest_framework import serializers

from users.models import User
from foodgram_backend.settings import EMAIL_MAX_LENGTH, USERNAME_MAX_LENTH

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'id', 'email',  'username', 'first_name', 'last_name')


class UserCreateSerializer(serializers.ModelSerializer):
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=USERNAME_MAX_LENTH,
        required=True
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        required=True,
    )
    first_name = serializers.CharField(
        required=True, max_length=USERNAME_MAX_LENTH)
    last_name = serializers.CharField(
        required=True, max_length=USERNAME_MAX_LENTH)

    class Meta:
        model = User
        fields = ('id',
                  'username',
                  'email',
                  'first_name',
                  'last_name',
                  'password')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Username "me" is not allowed.'
            )
        return value


class UserWithSubscriptionSerializer(serializers.ModelSerializer):
    is_subscripted = serializers.SerializerMethodField()

    def get_is_subscripted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers_set.filter(follower=request.user).exists()
        return False

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name',
            'last_name', 'is_subscripted'
        )


class TokenLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenLogoutSerializer(serializers.Serializer):
    pass
