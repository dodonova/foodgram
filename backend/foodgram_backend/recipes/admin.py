from django.contrib import admin

from recipes.models import (
    Recipe,
    Tag,
    MeasurementUnit,
    Ingredient,
    RecipeIngredient,
    RecipeTag,
    Favorites    
)

admin.site.register(Recipe)
admin.site.register(Tag)
admin.site.register(MeasurementUnit)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
admin.site.register(Favorites)