import base64
import logging
from venv import logger

from django.core.files.base import ContentFile
from rest_framework import serializers

from foodgram_backend.settings import (NAME_MAX_LENGTH)
from recipes.models import (Favorites, Ingredient, MeasurementUnit, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingList, Tag)
from users.serializers import UserGETSerializer

logging.basicConfig(level=logging.INFO)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')
        read_only_fields = ('id', 'name', 'color', 'slug')


class MeasurementUnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = MeasurementUnit
        fields = ('name',)


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id',)


class CustomIngredientSerializer(serializers.RelatedField):
    def to_internal_value(self, data):
        # logger.info(f'~~~~~ CustomIngredientSerializer to_internal_value: {data}, self: \n{self}\n')
        ingredient_id = data.get('id')
        ingredient = Ingredient.objects.get(pk=ingredient_id)
        # logger.info(f'~~~~~ CustomIngredientSerializer ingredient: {ingredient}\n')
        amount = data.get('amount')
        return {'ingredient': ingredient, 'amount': amount}

    def to_representation(self, value, obj):
        logger.info((f'~~~ CustomIngredientSerializer to_representation value:'
                     f'{type(value)}'
                     f'\n{value.id}, {value.name}, {value.measurement_unit}\n'))
        # logger.info(f'~~~~~ CustomIngredientSerializer  to_representation data: \n{data}\n')
        return {
            'id': value.id,
            'name': value.name,
            'measurement_unit': str(value.measurement_unit),
            'amount': 10
        }


class CustomTagSerializer(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'slug': value.slug,
            'color': value.color
        }


class RecipeIngredientGETSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient__id')
    name = serializers.CharField(source='ingredient__name', required=False)
    amount = serializers.FloatField()
    measurement_unit = serializers.CharField(
        source='measurement_unit__name', required=False)


class AmountRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        logger.info(f'~~~~~ AmountRelatedField to_representation value: {value.id, type(value)}')
        data = IngredientSerializer(value).data
        data['amount'] = 0
        return data

    def to_internal_value(self, data):
        return data


class RecipeSerializer(serializers.ModelSerializer):
    # ingredients = serializers.SerializerMethodField()
    ingredients = CustomIngredientSerializer(
        many=True,
        queryset=RecipeIngredient.objects.select_related('ingredient')
    )
    tags = CustomTagSerializer(many=True, queryset=Tag.objects.all())

    image = Base64ImageField(required=False, allow_null=True)
    author = UserGETSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        absctract = True
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
        )
        read_only_fields = (
            'id', 'author', 'is_favorited',
            'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorites.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ShoppingList.objects.filter(
                user=request.user,
                recipe=obj
            ).exists()
        return False

    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(
            recipe=obj).values(
                'ingredient__id', 'ingredient__name',
                'measurement_unit__name', 'amount'
                )
        return RecipeIngredientGETSerializer(ingredients, many=True).data

    def to_internal_value(self, data):
        # logger.info(f'~~~~~ RecipeSerializer to_internal_value: {data}, self: \n{self}\n')
        return super(RecipeSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        
        ingredients_data = validated_data.pop('ingredients', []) 

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags_data)

        # for tag_id in tags_data:

        logger.info(f'~~~~~ ingredients data: \n{ingredients_data}\n')

        recipe_ingredients = []

        for ingredient_data in ingredients_data:
            ingredient = ingredient_data['ingredient']
            amount = ingredient_data['amount']
            # Создаем или обновляем объект RecipeTag
            recipe_ingredient = RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient, amount=amount
            )
            # recipe_ingredient.save()
            recipe_ingredients.append(recipe_ingredient)
        return recipe

    

# class RecipeGETSerializer(RecipeSerializer):
#     pass


# class RecipeCreateSerilalizer(RecipeSerializer):
#     tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
#     ingredients = CustomIngredientSerializer(
#         many=True,
#         queryset=RecipeIngredient.objects.select_related('ingredient')
#     )

#     def create(self, validated_data):
#         tags_data = validated_data.pop('tags', [])  
#         ingredients_data = validated_data.pop('ingredients', []) 

#         recipe = Recipe.objects.create(**validated_data)

#         recipe.tags.set(tags_data)

#         logger.info(f'~~~~~ ingredients data: \n{ingredients_data}\n')

#         recipe_ingredients = []

#         for ingredient_data in ingredients_data:
#             ingredient = ingredient_data['ingredient']
#             amount = ingredient_data['amount']
#             # Создаем или обновляем объект RecipeTag
#             recipe_ingredient = RecipeIngredient.objects.create(
#                 recipe=recipe, ingredient=ingredient, amount=amount
#             )
#             # recipe_ingredient.save()
#             recipe_ingredients.append(recipe_ingredient)
#         return recipe

#     def to_representation(self, value):
#         logger.info(f'~~~~~ RecipeCreateSerilalizer  to_representation value: \n{type(value)} \n{value}\n{value.tags}')
        
#         return super(RecipeCreateSerilalizer, self).to_representation(value)