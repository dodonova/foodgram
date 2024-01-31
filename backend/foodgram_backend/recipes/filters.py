import logging
from venv import logger
from django_filters import rest_framework as filters
from users.models import User

from recipes.models import Ingredient, Recipe

logging.basicConfig(level=logging.INFO)


class StartsWithFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(**{f"{self.field_name}__startswith": value})
        return qs


class IngredientFilterSet(filters.FilterSet):
    name = StartsWithFilter(field_name='name')


# class IngredientFilterSet(filters.FilterSet):
#     class Meta:
#         model = Ingredient
#         fields = {
#             'name': ['exact']
#         }


class RecipeFilterSet(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.CharFilter(method='filter_tags')
    # is_in_shopping_cart = filters.BooleanFilter(method='filter_is_in_shopping_cart')

    def filter_tags(self, queryset, name, value):
        logger.info((f"~~~~~ FILTER:"
                     f"name: {name}\n"
                     f"value: {value}\n"
                     f"queryset: {queryset}\n"
                     f"self: {self}"))
        tags = value.split(',')
        queryset = queryset.filter(tags__slug__in=tags)
        return queryset

    # def filter_is_in_shopping_cart(self, queryset, name, value):
    #     is_in_shopping_cart_value = self.parent.serializer.context['is_in_shopping_cart']
    #     logger.info()
        

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
