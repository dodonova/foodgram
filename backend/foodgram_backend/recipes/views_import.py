import csv
import logging
from venv import logger

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
# from reportlab.pdfgen import canvas

from foodgram_backend.translat_dict import get_name as _
from users.permissions import IsAdminOrReadOnly, UsersAuthPermission

from recipes.filters import IngredientFilterSet, RecipeFilterSet
from recipes.models import (Favorites, Ingredient, MeasurementUnit,
                            Recipe, RecipeIngredient, Tag, ShoppingCart)
from recipes.serializers import (IngredientSerializer, LimitedRecipeSerializer,
                                 MeasurementUnitSerializer, RecipeSerializer,
                                 TagSerializer)


class ImportIngredientsView(APIView):
    serializer_class = IngredientSerializer(many=True)
    permission_classes = (IsAdminOrReadOnly, )

    def post(self, request, *args, **kwargs):
        data = request.data.get('data')
        serializer = IngredientSerializer(data=data, many=True)
        new_ids = []

        if serializer.is_valid():
            for item in serializer.validated_data:
                measurement_unit_name = item.get('measurement_unit')
                ingredient_name = item.get('name')
                
                measurement_unit, status = MeasurementUnit.objects.get_or_create(
                    name=measurement_unit_name)
            
                Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    measurement_unit=measurement_unit
                )
                new_ids.append(Ingredient.objects.get(name=ingredient_name).id)

            return Response(
                {'detail':
                    f'Ingredients imported successfully. Information: {new_ids}'},
                status=status.HTTP_201_CREATED)

        return Response(
            {
                'detail': f'Invalid data. Data: {data}',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
