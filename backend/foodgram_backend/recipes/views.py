import csv
import logging
from logging.handlers import RotatingFileHandler

from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from foodgram_backend.settings import (LOGS_BACKUP_COUNT, LOGS_MAX_BYTES,
                                       LOGS_ROOT)
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
from recipes.validators import validate_ingredients_data, validate_tags_data

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
handler = RotatingFileHandler(f"{LOGS_ROOT}{__name__}.log",
                              maxBytes=LOGS_MAX_BYTES,
                              backupCount=LOGS_BACKUP_COUNT)
formatter = logging.Formatter("%(name)s %(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


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

        if serializer.is_valid():
            serializer.save(author=self.request.user)
            logger.info(
                f"New recipe successfully created ID:{serializer.data['id']}"
            )
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        validate_ingredients_data(request)
        validate_tags_data(request)
        instance = self.get_object()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        RecipeTag.objects.filter(recipe=instance).delete()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def mark_recipe_post(self, model):
        """
        POST Method for marking recipe as favorite or adding to shopping cart.
        """
        self.serializer_class = LimitedRecipeSerializer
        try:
            recipe = self.get_object()
        except Exception:
            return Response({'error': 'No Recipe matches the given query.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user

        object, created = model.objects.get_or_create(recipe=recipe, user=user)
        if created:
            response_status = status.HTTP_201_CREATED
            return Response(
                LimitedRecipeSerializer(recipe).data,
                status=response_status
            )
        else:
            return Response({'error': 'Recipe is already in marked.'},
                            status=status.HTTP_400_BAD_REQUEST)

    def mark_recipe_delete(self, model):
        """
        DELETE Method for unmarking a recipe as favorite
        or removing from shopping cart.
        """
        self.serializer_class = LimitedRecipeSerializer
        try:
            recipe = self.get_object()
        except Exception:
            return Response({'error': 'No Recipe matches the given query.'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = self.request.user

        deleted, object = model.objects.filter(recipe=recipe,
                                               user=user).delete()
        if deleted == 0:
            return Response({'error': 'There is no sush record.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(
            LimitedRecipeSerializer(recipe).data,
            status=status.HTTP_204_NO_CONTENT
        )

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='favorite')
    def favorite(self, request, pk=None):
        """
        Endpoint for marking or unmarking a recipe as favorite.
        """
        if request.method == 'POST':
            return self.mark_recipe_post(Favorites)
        elif request.method == 'DELETE':
            return self.mark_recipe_delete(Favorites)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        """
        Endpoint for adding or removing a recipe from the shopping cart.
        """
        if request.method == 'POST':
            return self.mark_recipe_post(ShoppingCart)
        elif request.method == 'DELETE':
            return self.mark_recipe_delete(ShoppingCart)

    @action(detail=False,
            methods=['get'],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request, pk=None):
        """
        Endpoint for downloading the shopping cart as a CSV file.
        """
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
