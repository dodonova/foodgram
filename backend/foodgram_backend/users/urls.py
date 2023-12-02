from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import UserViewSet

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    # path('api/users/me/', CurrentUserViewSet, name='current-user'),
    path('api/', include(router_v1.urls)),
]
