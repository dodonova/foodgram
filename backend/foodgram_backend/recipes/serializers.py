from genericpath import exists
import logging
from venv import logger

import base64

from django.core.files.base import ContentFile
from foodgram_backend.settings import NAME_MAX_LENGTH
from rest_framework import serializers
from users.serializers import UserGETSerializer

from recipes.models import (Favorites, Ingredient, MeasurementUnit, Recipe,
                            RecipeIngredient, RecipeTag, ShoppingCart, Tag)
from recipes.validators import validate_ingredients_amount

logging.basicConfig(level=logging.INFO)


class Base64ImageField(serializers.ImageField):
    """
    Custom ImageField to handle base64 encoded images.
    """
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)

    def to_representation(self, value):
        return value.url


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


class RecipeTagSerializer(serializers.PrimaryKeyRelatedField):
    """
    Serializer for RecipeTag model.
    It is a nested  serializer for  RecipeSerializer field 'tags'.
    'tags' field should receive data in the form list[int] list of IDs
    and should response data in the form of list of JSON objects.
    """
    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'slug': value.slug,
            'color': value.color
        }


class RecipeIngredientSerializer(serializers.Serializer):
    """
    Serializer for RecipeIngredient model.
    It is a nested  serializer for  RecipeSerializer field 'ingredients'.
    """
    id = serializers.IntegerField()
    name = serializers.CharField(required=False, read_only=True)
    measurement_unit = serializers.CharField(required=False, read_only=True)
    amount = serializers.FloatField()

    def to_internal_value(self, data):
        amount = data.get('amount')
        validate_ingredients_amount(amount)
        return data

    def to_representation(self, value):
        logger.info(f"INGREDIENT to_representation:\n{value}\n{type(value)}\n")
        value.amount = None
        return super().to_representation(value)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = RecipeTagSerializer(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    author = UserGETSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=NAME_MAX_LENGTH)

    # To deploy to remote server:
    # cooking_time = serializers.CharField()

    class Meta:
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

    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients_data = validated_data.pop('ingredients', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tags_data:
            RecipeTag.objects.filter(recipe=instance).delete()
            instance.tags.set(tags_data)

        if ingredients_data:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            RecipeIngredient.objects.bulk_create([
                RecipeIngredient(
                    recipe=instance,
                    ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                    amount=ingredient.get('amount')
                )
                for ingredient in ingredients_data
            ])
        return instance

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient.get('id')),
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients
        ])
        logger.info("~~~ RecipeIngredient created \n")
        return recipe

    def to_representation(self, value):
        recipe_id = value.id
        json_data = super().to_representation(value)
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe=recipe_id).values('ingredient', 'amount')

        for ingredient in json_data['ingredients']:
            current_amount = recipe_ingredients.get(
                ingredient=ingredient['id']).get('amount')
            ingredient['amount'] = current_amount
        return json_data

    def nested_list_validate(self, nested_list, model):
        """  Validate data in the fields 'ingredient' or 'tags'

        Args:
            nested_list ([int]): list of IDs
            model (_type_): model Ingredient of Tag
        """
        model_name = model.__name__
        if len(nested_list) == 0:
            raise serializers.ValidationError(
                '{model_name} list cannot be empty.'
            )

        if len(set(nested_list)) != len(nested_list):
            raise serializers.ValidationError(
                f'Duplicate {model_name} id error.'
            )

        for id in nested_list:
            if not model.objects.filter(pk=id).exists():
                raise serializers.ValidationError(
                    f"There is no {model_name} with id={id}"
                )

    def is_valid(self, *, raise_exception=False):
        fields = ['name', 'image', 'text',
                  'cooking_time', 'tags', 'ingredients']
        for field in self.initial_data:
            if self.initial_data.get(field, []):
                fields.remove(field)

        if fields:
            raise serializers.ValidationError(f'Required fields: {fields}')

        if len(self.initial_data['name']) > NAME_MAX_LENGTH:
            raise serializers.ValidationError('Too long name.')

        tags_id = self.initial_data.get('tags', [])
        ingredients_data = self.initial_data.get('ingredients', [])
        ingredients_id = [ingredient['id'] for ingredient in ingredients_data]

        self.nested_list_validate(tags_id, Tag)
        self.nested_list_validate(ingredients_id, Ingredient)
        return super().is_valid(raise_exception=False)

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


class LimitedRecipeSerializer(serializers.ModelSerializer):
    """
    Serializer for Recipe model for shortened representation.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRecipesSerializer(UserGETSerializer):
    """
    Serializer for User model with related recipes.
    """
    recipes = LimitedRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserGETSerializer.Meta):
        fields = (
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_subscribed',
            'recipes_count', 'recipes'
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def to_representation(self, value):
        recipes_limit = self.context.get('recipes_limit')
        ret = super().to_representation(value)

        if recipes_limit is not None and recipes_limit.isdigit():
            if int(recipes_limit) > 0:
                ret["recipes"] = ret["recipes"][:int(recipes_limit)]

        return ret
