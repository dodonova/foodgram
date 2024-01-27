import base64
import logging
from multiprocessing import context
from venv import logger

from django.core.files.base import ContentFile
from rest_framework import serializers

from foodgram_backend.settings import (NAME_MAX_LENGTH)
from recipes.models import (Favorites, Ingredient, MeasurementUnit, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)
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


class AmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('amount',)


class RecipeIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient__id')
    name = serializers.CharField(source='ingredient__name')
    amount = serializers.FloatField()
    measurement_unit = serializers.CharField(
        source='measurement_unit__name')
    
    # measurement_unit = serializers.CharField()
    # amount = None

    # def __init__(self, instance=None, data=None, **kwargs):
    #     super(RecipeIngredientSerializer, self).__init__()
    #     # logger.info(f'RecipeIngredient DATA: {self.data}')

    # def to_representation(self, instance):
    #     # logger.info(f'RecipeIngredient INSTANCE: {instance}')
    #     # logger.info(f'RecipeIngredient CONTEXT: {self.context}')
    #     # logger.info(f'RecipeIngredient FIELDS: {self.fields}')

    #     if 'recipe' in self.context:
    #         recipe_id = self.context.get('recipe')
    #         recipe = Recipe.objects.get(pk=recipe_id)
    #         obj = RecipeIngredient.objects.filter(
    #             recipe=recipe, ingredient=instance
    #         ).first()
    #         logger.info(f'RecipeIngredient obj.data: {obj.amount}')
    #         self.fields['amount'] = AmountSerializer(obj)

    #     return super(RecipeIngredientSerializer, self).to_representation(instance)

    # class Meta:
    #     model = Ingredient
    #     fields = ('id', 'name', 'measurement_unit', 'amount')     


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    # ingredients = RecipeIngredientSerializer(many=True)
    tags = TagSerializer(many=True)

    image = Base64ImageField(required=False, allow_null=True)
    author = UserGETSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    def __init__(self, instance, **kwargs):
        super(RecipeSerializer, self).__init__()
        # logger.info(f'Recipe  SELF: {self}')
        # logger.info(f'Recipe  DATA: {self.data}')
        # logger.info(f'Recipe  INSTANCE: {instance}')

    def to_representation(self, instance):
        # logger.info(f'Recipe SELF: {self}')
       
               
        # recipe_id = instance.id
        # ingredient_context = {'recipe': recipe_id}
        
        # ingredient_data = RecipeIngredientSerializer(
        #     instance=instance.ingredients.all(),
        #     context=ingredient_context,
        #     many=True
        # ).data
        # data = super(RecipeSerializer, self).to_representation(instance)
        # logger.info(f'Recipe to_representation DATA: {data}')
        # data['ingredients'] = ingredient_data
        # return data

        ingredients = RecipeIngredient.objects.filter(
            recipe=instance).values(
                'ingredient__id', 'ingredient__name',
                'measurement_unit__name', 'amount'
                )

        ingredients_data = RecipeIngredientSerializer(
            ingredients, many=True
        ).data

        data = super(RecipeSerializer, self).to_representation(instance)
        data['ingredients'] = ingredients_data
        return data

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
            return ShoppingCart.objects.filter(
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
        return RecipeIngredientSerializer(ingredients, many=True).data


class RecipeGETSerializer(RecipeSerializer):
    pass


class RecipeCreateSerilalizer(RecipeSerializer):
    pass


