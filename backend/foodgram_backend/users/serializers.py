from dataclasses import fields
from rest_framework import serializers

from users.models import User, Subscription


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
