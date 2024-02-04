import csv
import logging
from venv import logger

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from foodgram_backend.translat_dict import get_name as _
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from users.permissions import RecipeActionsPermission

from recipes.filters import IngredientFilterSet, RecipeFilterSet
from recipes.models import (Favorites, Ingredient, MeasurementUnit, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)
from recipes.serializers import (IngredientSerializer, LimitedRecipeSerializer,
                                 MeasurementUnitSerializer, RecipeSerializer,
                                 TagSerializer)
from recipes.validators import validate_recipe_data


logging.basicConfig(level=logging.INFO)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class MeasurementUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MeasurementUnit.objects.all()
    serializer_class = MeasurementUnitSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilterSet


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilterSet
    permission_classes = [RecipeActionsPermission]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid()
            serializer.save(author=self.request.user)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        except Exception as err:
            return Response(
                {"error:": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if not validate_recipe_data(request):
            return Response(
                {'error': 'Ingredients and tags cannot be an empty list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        instance = self.get_object()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeTag.objects.filter(recipe=instance).delete()
        serializer = self.get_serializer(
            instance, data=request.data, partial=False
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        except Exception as err:
            return Response(
                {"error:": str(err)}, status=status.HTTP_400_BAD_REQUEST)

    def mark_recipe(self, request, model):
        self.serializer_class = LimitedRecipeSerializer
        try:
            recipe = self.get_object()
        except Exception as err:
            logger.error(f'RECIPE NOT FOUND: {err}\n')
            return Response({'error': 'No Recipe matches the given query.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user

        if request.method == 'POST':
            object, created = model.objects.get_or_create(recipe=recipe,
                                                          user=user)
            if created:
                response_status = status.HTTP_201_CREATED
                return Response(
                    LimitedRecipeSerializer(recipe).data,
                    status=response_status
                )
            else:
                return Response({'error': 'Recipe is already in marked.'},
                                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            result, obj = model.objects.filter(recipe=recipe,
                                               user=user).delete()
            if result == 0:
                return Response({'error': 'There is no sush record.'},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(
                LimitedRecipeSerializer(recipe).data,
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        return self.mark_recipe(request, Favorites)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        return self.mark_recipe(request, ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request, pk=None):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="data.csv"'

        user = self.request.user
        recipes_in_shopping_cart = ShoppingCart.objects.filter(
            user=user).values('recipe')
        ingredients = RecipeIngredient.objects.filter(
            recipe__in=recipes_in_shopping_cart)
        shopping_cart = (
            ingredients
            .values('ingredient__name', 'measurement_unit__name')
            .annotate(
                total_amount=Sum('amount'),
            )
        )
        writer = csv.writer(response)
        title_row = (_('Ingredient'), _('Amount'), _('Measurement Unit'))
        writer.writerow(title_row)
        for record in shopping_cart:
            record_tuple = (
                record.get('ingredient__name'),
                record.get('total_amount'),
                record.get('measurement_unit__name'),
            )
            writer.writerow(record_tuple)

        return response
