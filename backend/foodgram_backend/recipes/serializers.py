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


class RecipeIngredientSerializer(serializers.RelatedField):
    def to_internal_value(self, data, recipe_id=1):
        ingredient = Ingredient.objects.get(pk=data.get('id'))
        recipe = Recipe.objects.get(pk=recipe_id)
        obj = RecipeIngredient.objects.create(
            recipe=recipe, ingredient=ingredient, amount=data.get('amount')
        )
        obj.save()
        return obj
    
    def to_representation(self, value):
        return {
            'id': value.ingredient.id,
            'name': value.ingredient.name,
            'measurement_unit': value.ingredient.measurement_unit.name,
            'amount': value.amount
        }


class CustomTagSerializer(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'slug': value.slug,
            'color': value.color
        }


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True,
        queryset=RecipeIngredient.objects.select_related('ingredient'),
        source='recipe_ingredients'
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

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        recipe_ingredients_data = validated_data.pop('recipe_ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        recipe.recipe_ingredients.set(recipe_ingredients_data)
        return recipe
