from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import Ingredient, MeasurementUnit
from recipes.serializers import IngredientSerializer
from users.permissions import IsAdminOrReadOnly


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
                measurement_unit, st = MeasurementUnit.objects.get_or_create(
                    name=measurement_unit_name)

                Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    measurement_unit=measurement_unit
                )
                new_ids.append(Ingredient.objects.get(name=ingredient_name).id)

            return Response(
                {'detail':
                    f'Ingredients imported successfully: {new_ids}'},
                status=status.HTTP_201_CREATED)

        return Response(
            {
                'detail': f'Invalid data. Data: {data}',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
