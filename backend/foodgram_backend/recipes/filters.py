from django_filters import rest_framework as filters
from users.models import User

from recipes.models import Favorites, Recipe, ShoppingCart, Tag


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
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

    def filter_favorites_or_shopping_cart(self, queryset, name, value, model):
        if self.request.user.is_authenticated:
            if value:
                recipes_id = model.objects.filter(
                    user=self.request.user).values('recipe')
                queryset = Recipe.objects.filter(id__in=recipes_id)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        return self.filter_favorites_or_shopping_cart(
            queryset, name, value, ShoppingCart
        )

    def filter_is_favorited(self, queryset, name, value):
        return self.filter_favorites_or_shopping_cart(
            queryset, name, value, Favorites
        )
