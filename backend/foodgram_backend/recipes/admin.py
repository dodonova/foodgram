from django.contrib import admin

from recipes.models import (Favorites, Ingredient, MeasurementUnit, Recipe,
                            ShoppingCart, Tag)


class CustomShoppingCart(admin.ModelAdmin):
    model = ShoppingCart
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


class TagInline(admin.TabularInline):
    model = Recipe.tags.through


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'ingredients_list',
        'tags_list', 'author', 'cooking_time',
        'image', 'pub_date', 'portions'
    )
    list_editable = (
        'cooking_time', 'image', 'portions'
    )
    list_filter = ('tags', 'author')

    inlines = (IngredientInline, TagInline)

    def ingredients_list(self, obj):
        return ", ".join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )
    ingredients_list.short_description = ("Ingredients")

    def tags_list(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])
    tags_list.short_description = ("Tags")


class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'measurement_unit'
    )
    list_editable = (
        'measurement_unit',
    )


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'slug', 'color'
    )
    list_editable = ('slug', 'color')


class MeasurementUnitAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    list_editable = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(MeasurementUnit, MeasurementUnitAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(ShoppingCart, CustomShoppingCart)
admin.site.register(Favorites, FavoritesAdmin)
