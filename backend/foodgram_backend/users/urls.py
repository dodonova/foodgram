from django.urls import include, path
from rest_framework.routers import DefaultRouter
from users.views import UserSubscriptionsViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path(
        'api/users/subscriptions/',
        UserSubscriptionsViewSet.as_view({'get': 'list'}),
        name='user-subscriptions'),
    path(
        'api/auth/token/login/',
        UserViewSet.as_view({'post': 'token_login'}),
        name='user-token-login'),
    path(
        'api/auth/token/logout/',
        UserViewSet.as_view({'post': 'token_logout'}),
        name='user-token-logout'),
    path('api/', include(router.urls)),
]
