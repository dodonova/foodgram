from django_filters import rest_framework as filters
from users.models import User

from recipes.models import Recipe


class StartsWithFilter(filters.CharFilter):
    def filter(self, qs, value):
        if value:
            return qs.filter(**{f"{self.field_name}__startswith": value})
        return qs


class IngredientFilterSet(filters.FilterSet):
    name = StartsWithFilter(field_name='name')


class RecipeFilterSet(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.CharFilter(method='filter_tags')

    def filter_tags(self, queryset, name, value):
        tags = value.split(',')
        queryset = queryset.filter(tags__slug__in=tags)
        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags']
