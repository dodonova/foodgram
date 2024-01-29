from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (IngredientViewSet, MeasurementUnitViewSet,
                           RecipeViewSet, TagViewSet)
from recipes.views_import import ImportIngredientsView

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tags')
router.register(
    'measurment-units', MeasurementUnitViewSet,
    basename='measurment_units')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('api/', include(router.urls)),
    path(
        'api/import/ingredients/',
        ImportIngredientsView.as_view(),
        name='import-ingredients')
]
