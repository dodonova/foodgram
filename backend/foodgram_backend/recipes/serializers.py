import base64
from crypt import methods
from importlib.util import source_hash
import logging
from curses.ascii import US
from operator import methodcaller
from os import system

from django.core.files.base import ContentFile
from rest_framework import serializers

from foodgram_backend.settings import (NAME_MAX_LENGTH)
from recipes.models import (Ingredient, MeasurementUnit, Recipe,
                            RecipeIngredient, RecipeTag, Tag)
from users.serializers import UserWithSubscriptionSerializer

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

    def create(self, validated_data):
        name = validated_data.get('name')
        measurement_unit_name = validated_data.get('measurement_unit')
        measurement_unit, status = MeasurementUnit.objects.get_or_create(
            name=measurement_unit_name)
        ingredient = Ingredient.objects.create(
            measurement_unit=measurement_unit,
            name=name
        )
        return ingredient


class RecipeIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient__id')
    name = serializers.CharField(
        max_length=NAME_MAX_LENGTH, source='ingredient__name')
    amount = serializers.FloatField()
    measurement_unit = serializers.CharField(
        max_length=NAME_MAX_LENGTH, source='measurement_unit__name')


class RecipeGETSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, required=False)
    image = Base64ImageField(required=False, allow_null=True)
    # image_url = serializers.SerializerMethodField(
    #     'get_image_url',
    #     read_only=True,
    # )
    author = UserWithSubscriptionSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',
            # 'image_url'
        )
        read_only_fields = ('id', 'author',)

    def get_is_favorited(self, obj):
        return True

    def get_is_in_shopping_cart(self, obj):
        return True

    def get_ingredients(self, obj):
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe=obj).values(
                'ingredient__id', 'ingredient__name', 'measurement_unit__name', 'amount')
        return RecipeIngredientSerializer(recipe_ingredients, many=True).data

    # def get_image_url(self, obj):
    #     if obj.image:
    #         return obj.image.url
    #     return None

    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     ingredients_data = representation.pop('ingredients')
    #     representation['ingredients'] = []
    #     for ingredient_data in ingredients_data:
    #         ingredient = ingredient_data['ingredient']
    #         ingredient_representation = {
    #             'id': ingredient['id'],
    #             'name': ingredient['name'],
    #             'measurement_unit': ingredient['measurement_unit']['name'],
    #             'amount': ingredient_data['amount']
    #         }
    #         representation['ingredients'].append(ingredient_representation)
    #     return representation


# class RecipeSerializer(serializers.ModelSerializer):
#     ingredients = IngredientGETSerializer(many=True, read_only=True)
#     tags = TagSerializer(many=True, required=False)
#     image = Base64ImageField(required=False, allow_null=True)
#     image_url = serializers.SerializerMethodField(
#         'get_image_url',
#         read_only=True,
#     )
#     author = UserWithSubscriptionSerializer(read_only=True)
    
#     class Meta:
#         model = Recipe
#         fields = (
#             'id',
#             'tags',
#             'author',
#             'ingredients',
#             # 'is_favorited',
#             # 'is_in_shopping_cart',
#             'name',
#             'image',
#             'image_url',
#             'text',
#             'cooking_time'
#         )
#         read_only_fields = ('author',)

#     def get_image_url(self, obj):
#         if obj.image:
#             return obj.image.url
#         return None

#     def create(self, validated_data):
#         if 'ingredients' in self.initial_data:
#             ingredients = validated_data.pop('ingredients')

#         if 'tags' in self.initial_data:
#             tags = validated_data.pop('tags')
        
#         recipe = Recipe.objects.create(**validated_data)

#         if ingredients:
#             for ingredient in ingredients:
#                 current_ingredient, status = Ingredient.objects.get_or_create(
#                     **ingredient)
#                 RecipeIngredient.objects.create(
#                     ingredient=current_ingredient, recipe=recipe)

#         if 'tags' in self.initial_data:
#             for tag_id in tags:
#                 current_tag = RecipeTag.objects.filter(pk=tag_id).first()
#                 if current_tag:
#                     RecipeTag.objects.create(recipe=recipe, tag=current_tag)
#         return recipe

