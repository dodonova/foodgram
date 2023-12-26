import base64
from curses.ascii import US
from os import system

from django.core.files.base import ContentFile
from rest_framework import serializers
from transliterate import slugify

from recipes.models import (Ingredient, MeasurementUnit, Recipe,
                            RecipeIngredient, RecipeTag, Tag)

from users.serializers import UserWithSubscriptionSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class MeasurementUnitSerializer(serializers.ModelSerializer):

    class Meta:
        model = MeasurementUnit
        fields = ('id', 'name')


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField()

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'slug', 'measurement_unit')
        read_only_fields = ('id', 'slug')

    def create(self, validated_data):
        name = validated_data.get('name')
        slug = (slugify(name) if slugify(name) is not None
                else name.replace(' ', '-'))
        measurement_unit_name = validated_data.get('measurement_unit')
        measurement_unit, status = MeasurementUnit.objects.get_or_create(
            name=measurement_unit_name)
        ingredient = Ingredient.objects.create(
            measurement_unit=measurement_unit,
            name=name, slug=slug
        )
        return ingredient



# class IngredientImportSerializer(serializers.Serializer):
#     data = IngredientSerializer(many=True)


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    image = Base64ImageField(required=False, allow_null=True)
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )
    author = UserWithSubscriptionSerializer(read_only=True)
    
    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            # 'is_favorited',
            # 'is_in_shopping_cart',
            'name',
            'image',
            'image_url',
            'text',
            'cooking_time'
        )
        read_only_fields = ('author',)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None

    def create(self, validated_data):
        ingredients = None
        tags = None
        
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')

        if 'tags' in self.initial_data:
            tags = validated_data.pop('tags')
        
        recipe = Recipe.objects.create(**validated_data)

        if ingredients:
            for ingredient in ingredients:
                current_ingredient, status = Ingredient.objects.get_or_create(
                    **ingredient)
                RecipeIngredient.objects.create(
                    ingredient=current_ingredient, recipe=recipe)

        if 'tags' in self.initial_data:
            for tag_id in tags:
                current_tag = RecipeTag.objects.filter(pk=tag_id).first()
                if current_tag:
                    RecipeTag.objects.create(recipe=recipe, tag=current_tag)
        return recipe
