import logging

from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

# from recipes.serializers import IngredientImportSerializer

from recipes.models import Ingredient, MeasurementUnit, Recipe, Tag
from recipes.serializers import (IngredientSerializer,
                                 MeasurementUnitSerializer, RecipeGETSerializer,
                                 TagSerializer)
from users.permissions import IsAdminOrReadOnly

logging.basicConfig(level=logging.INFO)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = None


class MeasurementUnitViewSet(viewsets.ModelViewSet):
    queryset = MeasurementUnit.objects.all()
    serializer_class = MeasurementUnitSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Recipe.objects.all()
    serializer_class = RecipeGETSerializer
    pagination_class = PageNumberPagination

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    # def retrieve(self, request, *args, **kwargs):
    #     logging.warning(f"GET запрос recipes.")
    #     return super().retrieve(request, *args, **kwargs)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )
    pagination_class = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save()




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