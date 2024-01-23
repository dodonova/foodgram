from dataclasses import field
from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag
from users.models import User


class StartsWithFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(**{f"{self.field_name}__startswith": value})
        return qs


class IngredientFilterSet(filters.FilterSet):
    name = StartsWithFilter(field_name='name')


class RecipeFilterSet(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tag__name',
        to_field_name='tags'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
