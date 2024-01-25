import logging
from venv import logger
from xmlrpc.client import ResponseError

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework import filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action



# from recipes.serializers import IngredientImportSerializer

from recipes.models import Ingredient, MeasurementUnit, Recipe, Tag, Favorites
from recipes.serializers import (IngredientSerializer,
                                 MeasurementUnitSerializer,
                                 RecipeSerializer,
                                 TagSerializer,
                                 LimitedRecipeSerializer)
from recipes.filters import IngredientFilterSet, RecipeFilterSet
from users.permissions import IsAdminOrReadOnly, UsersAuthPermission

logging.basicConfig(level=logging.INFO)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class MeasurementUnitViewSet(viewsets.ModelViewSet):
    queryset = MeasurementUnit.objects.all()
    serializer_class = MeasurementUnitSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilterSet

    # def get_serializer_class(self):
    #     if self.action in ('list', 'retireve'):
    #         return RecipeGETSerializer
    #     elif self.action in ('create', 'update'):
    #         return RecipeCreateSerilalizer

    def perform_create(self, serializer):
        # serializer_class = RecipeCreateSerilalizer
        serializer.save(author=self.request.user)

    # def retrieve(self, request, *args, **kwargs):
    #     logging.warning(f"GET запрос recipes.")
    #     return super().retrieve(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post'],
        url_path='favorite',
        permission_classes=[UsersAuthPermission]
    )
    def favorite(self, request, pk=None):
        self.serializer_class = LimitedRecipeSerializer
        try:
            recipe = self.get_object()
        except Exception as err:
            logger.error(f'RECIPE NOT FOUND: {err}\n')
            return Response(
                        {'error': 'No Recipe matches the given query.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        user = self.request.user
        favorite, created = Favorites.objects.get_or_create(
            recipe=recipe, user=user
        )
        if created:
            response_status = status.HTTP_201_CREATED
        else:
            response_status = status.HTTP_200_OK

        return Response(
            LimitedRecipeSerializer(recipe).data,
            status=response_status
        )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    # permission_classes = (IsAdminOrReadOnly, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientFilterSet




    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(
    #         serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # def perform_create(self, serializer):
    #     serializer.save()


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