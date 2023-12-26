from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (
    TagViewSet,
    MeasurementUnitViewSet,
    RecipeViewSet,
    IngredientViewSet,
    ImportIngredientsView
)

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register(
    'measurment-units',
    MeasurementUnitViewSet,
    basename='measurment_units')
router_v1.register('recipes', RecipeViewSet, basename='recipes')
router_v1.register('ingredients', IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('api/', include(router_v1.urls)),
    path(
        'api/import/ingredients/',
        ImportIngredientsView.as_view(),
        name='import-ingredients'),

]
