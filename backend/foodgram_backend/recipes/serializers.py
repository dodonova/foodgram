import base64

from django.core.files.base import ContentFile
from foodgram_backend.settings import NAME_MAX_LENGTH
from rest_framework import serializers
from users.serializers import UserGETSerializer

from recipes.models import (Favorites, Ingredient, MeasurementUnit, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from recipes.validators import validate_ingredients_amount


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


class LimitedRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeTagSerializer(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        return {
            'id': value.id,
            'name': value.name,
            'slug': value.slug,
            'color': value.color
        }


class RecipeIngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(required=False)

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit')

    def to_internal_value(self, data):
        ingredient = Ingredient.objects.get(pk=data.get('id'))
        return ingredient


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = RecipeTagSerializer(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    author = UserGETSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    name = serializers.CharField(max_length=NAME_MAX_LENGTH)
    cooking_time = serializers.CharField()

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

    def create_or_update(self, validated_data, instance=None):
        tags_data = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        amounts = [
            record.get('amount')
            for record
            in self.initial_data.get('ingredients')
        ]

        if instance:
            recipe = instance
        else:
            recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)

        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(recipe=recipe,
                             ingredient=ingredient,
                             amount=amount)
            for (ingredient, amount)
            in zip(ingredients, amounts)
        ])
        return recipe

    def update(self, instance, validated_data):
        return self.create_or_update(validated_data, instance)

    def create(self, validated_data):
        return self.create_or_update(validated_data)

    def to_internal_value(self, data):
        if data.get('ingredients') is not None:
            for row in data.get('ingredients'):
                amount = row.get('amount')
                validate_ingredients_amount(amount)

        ret = super().to_internal_value(data)
        return ret

    def to_representation(self, value):
        recipe_id = value.id
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe=recipe_id).values('ingredient', 'amount')
        json_data = super().to_representation(value)

        for ingredient in json_data['ingredients']:
            current_amount = recipe_ingredients.get(
                ingredient=ingredient['id']).get('amount')
            ingredient['amount'] = current_amount
        return json_data

    def is_valid(self, *, raise_exception=False):
        tags_data = self.initial_data.get('tags', [])
        if len(tags_data) == 0:
            raise serializers.ValidationError('Tags list cannot be empty.')
        if len(set(tags_data)) != len(tags_data):
            raise serializers.ValidationError('Duplicate tags error.')
        ingredients_data = self.initial_data.get('ingredients', [])
        if len(ingredients_data) == 0:
            raise serializers.ValidationError(
                'Ingredients list cannot be empty.'
            )
        return super().is_valid(raise_exception=False)


class UserRecipesSerializer(UserGETSerializer):
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
