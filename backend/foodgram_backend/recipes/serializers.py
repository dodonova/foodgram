from dataclasses import fields
from rest_framework import serializers

from recipes.models import (
    Tag,
    MeasurementUnit
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class MeasurementUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasurementUnit
        fields = '__all__'
