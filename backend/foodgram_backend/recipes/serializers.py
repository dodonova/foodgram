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


class RecipeIngredientGETSerializer(serializers.Serializer):
    id = serializers.IntegerField(source='ingredient__id')
    name = serializers.CharField(source='ingredient__name', required=False)
    amount = serializers.FloatField()
    measurement_unit = serializers.CharField(
        source='measurement_unit__name', required=False)
    
    # class Meta:
    #     model = Ingredient
    #     fields = ('id', 'name', 'measurement_unit', 'amount')   
    #     read_only_fealds = ('name', 'measurement_unit') 


class RecipeIngredientCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.FloatField()
    
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


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)

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


class RecipeGETSerializer(RecipeSerializer):
    pass


class AmountRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        logger.info(f'AmountRelatedField to_representation value: {value.id, type(value)}')
        data = IngredientSerializer(value).data
        data['amount'] = 0
        return data
    
    def to_internal_value(self, data):
        # logger.info(f'to_internal_value: {data}, self: {self}')
        # recipe_ingredient = RecipeIngredient.objects.get(pk=instance.id)
            # RecipeIngredient.objects.create(
            #     recipe=recipe,
            #     ingredient=ingredient,
            #     amount=ingredient['amount'],
            # )
        # return recipe
        return data


class RecipeCreateSerilalizer(RecipeSerializer):
    # tags = serializers.ListField(child=serializers.IntegerField())
    ingredients = AmountRelatedField(many=True, queryset=RecipeIngredient.objects.all())
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])  
        ingredients_data = validated_data.pop('ingredients', []) 

        recipe = Recipe.objects.create(**validated_data)

        recipe.tags.set(tags_data)

        # logger.info(f'ingredient data: {ingredients_data}')

        for ingredient in ingredients_data:
            # logger.info(f'RecipeCreateSerilalizer: {self}')            
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=ingredient['id']),
                amount=ingredient['amount'],
            )
        return recipe



    # def create(self, validated_data):
    #     ingredients = validated_data.pop('ingredients')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)

    #     logger.info(f'RecipeCreate INGREDIENTS: {ingredients}')
 
    #     for ingredient_data in ingredients:
    #         ingredient = Ingredient.objects.get(id=ingredient_data['id'])
    #         amount = ingredient_data['amount']
    #         RecipeIngredient.objects.create(
    #             recipe=recipe,
    #             ingredient=ingredient,
    #             amount=amount,
    #         )
    #     logger.info(f'TAGS: {tags} |  {type(tags)}')
    #     for tag_id in tags:
    #         logger.info(f'TAG_ID: {tag_id} | {type(tag_id)}')
    #         # tag_id = tag_id['tag']
    #         tag = Tag.objects.get(id=tag_id)
    #         RecipeTag.objects.create(recipe=recipe, tag=tag)

    #     logger.info(f'Recipe: {type(recipe)}\n{recipe}')
    #     # logger.info(f'Recipe ingredients: {recipe.name}')

    #     return recipe



    # def create(self, validated_data):
        # ingredients = None
        # tags = None

        # if 'ingredients' in self.initial_data:
        #     ingredients = validated_data.pop('ingredients')

        # if 'tags' in self.initial_data:
        #     tags = validated_data.pop('tags')

        # recipe = Recipe.objects.create(**validated_data)

        # if ingredients:
        #     for ingredient in ingredients:
        #         current_ingredient, status = Ingredient.objects.get_or_create(
        #             **ingredient)
        #         RecipeIngredient.objects.create(
        #             ingredient=current_ingredient, recipe=recipe)

        # if 'tags' in self.initial_data:
        #     for tag_id in tags:
        #         current_tag = Tag.objects.filter(pk=tag_id).first()
        #         if current_tag:
        #             RecipeTag.objects.create(recipe=recipe, tag=current_tag)

        # logger.info(f'\n\n\n\nDONE')
        # return recipe