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


class RecipeIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient__id')
    name = serializers.CharField(
        max_length=NAME_MAX_LENGTH, source='ingredient__name')
    amount = serializers.FloatField()
    measurement_unit = serializers.CharField(
        max_length=NAME_MAX_LENGTH, source='measurement_unit__name')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'amount', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    # ingredients = RecipeIngredientSerializer(many=True)
    
    tags = TagSerializer(many=True)
    # tags = serializers.SerializerMethodField()

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
        return RecipeIngredientSerializer(ingredients, many=True).data


class RecipeGETSerializer(RecipeSerializer):
    pass


class RecipeCreateSerilalizer(RecipeSerializer):
    # pass
    tags = serializers.ListField(child=serializers.IntegerField())

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
 
        for ingredient_data in ingredients:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            amount = ingredient_data['amount']
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount=amount,
            )

        logger.log(f'TAGS: {tags} |  {type(tags)}')
        for tag_id in tags:
            logger.log(f'TAG_ID: {tag_id} | {type(tag_id)}')
            # tag_id = tag_id['tag']
            tag = Tag.objects.get(id=tag_id)
            RecipeTag.objects.create(recipe=recipe, tag=tag)

        return recipe
