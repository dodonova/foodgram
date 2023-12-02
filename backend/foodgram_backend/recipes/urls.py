from django.urls import include, path
from rest_framework.routers import DefaultRouter

from recipes.views import (
    TagViewSet,
    MeasurementUnitViewSet,
)

router_v1 = DefaultRouter()
router_v1.register('tags', TagViewSet, basename='tags')
router_v1.register(
    'measurment-units',
    MeasurementUnitViewSet,
    basename='measurment_units')

urlpatterns = [
    path('api/', include(router_v1.urls)),
]
