from django.contrib import admin

from recipes.models import (
    Recipe,
    Tag,
    MeasurementUnit,
    Ingredient,
    RecipeIngredient,
    # RecipeTag,
    Favorites    
)


# admin.site.site_header = 'Рецепты'
# admin.site.site_title = 'Рецепты'


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredient.through


class TagInline(admin.TabularInline):
    model = Recipe.tag.through


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'ingredients_list', 'tags_list',
        'author', 'cooking_time', 'image',
        'pub_date', 'portions'
    )
    list_editable = (
        'cooking_time', 'image',     'portions'
    )
    list_filter = ('tag', )

    inlines = (IngredientInline, TagInline)

    def ingredients_list(self, obj):
        return ", ".join([ingredient.name for ingredient in obj.ingredient.all()])
    ingredients_list.short_description = ("Ingredients")

    def tags_list(self, obj):
        return ", ".join([tag.name for tag in obj.tag.all()])
    tags_list.short_description = ("Tags")


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',  'measurement_unit'
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
# admin.site.register(RecipeIngredient)
# admin.site.register(RecipeTag)
admin.site.register(Favorites)
