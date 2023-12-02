from django.shortcuts import render
from rest_framework import viewsets

from recipes.models import (
    # Ingredient,
    # Recipe,
    Tag,
    MeasurementUnit,
)
from recipes.serializers import (
    TagSerializer,
    MeasurementUnitSerializer
)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class MeasurementUnitViewSet(viewsets.ModelViewSet):
    queryset = MeasurementUnit.objects.all()
    serializer_class = MeasurementUnitSerializer
