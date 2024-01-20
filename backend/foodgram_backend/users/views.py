from django.db import IntegrityError
from rest_framework import mixins, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import (
    PageNumberPagination,
    LimitOffsetPagination)
from rest_framework.response import Response

from users.models import Subscription, User
from users.permissions import UsersAuthPermission
from users.serializers import (TokenLoginSerializer,  # UserSerializer,
                               TokenLogoutSerializer, UserCreateSerializer,
                               UserGETSerializer)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserGETSerializer
    permission_classes = [UsersAuthPermission]
    pagination_class = LimitOffsetPagination
    # page_size = 3

    def create(self, request, *args, **kwargs):
        self.serializer_class = UserCreateSerializer

        try:
            response = super().create(request, *args, **kwargs)
            # Выводим информацию о созданном пользователе
            # created_user_data = response.data
            # print(f"User created: {created_user_data}")
            return response
            # return super().create(request, *args, **kwargs)

        except IntegrityError as e:
            error_message = str(e)
            if 'unique constraint' in error_message.lower():
                return Response(
                    {'detail':
                        'User with this username or email already exists.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    {'detail':
                        'An error occurred while processing your request.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


    def token_login(self, request):
        serializer = TokenLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])
        token, _ = Token.objects.get_or_create(user=user)

        # Set the token in the response header
        response = Response({'auth_token': token.key}, status=status.HTTP_200_OK)
        response['Authorization'] = f'Token {token.key}'

        return response


    @action(detail=False, methods=['post'], url_path='token/logout')
    def token_logout(self, request):
        serializer = TokenLogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get', 'patch'])
    def me(self, request):
        serializer = UserGETSerializer(
            request.user,
            data=request.data,
            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='subscribe'
    )
    def subscribe_user(self, request, pk=None):
        following_user = self.get_object()
        follower_user = request.user

        if request.method == 'DELETE':
            Subscription.objects.filter(
                follower=follower_user,
                following=following_user
            ).delete()
            return Response(
                {'detail': 'Successfully unsubscribed.'},
                status=status.HTTP_200_OK
            )

        if request.method == 'POST':
            subscription, created = Subscription.objects.get_or_create(
                follower=follower_user,
                following=following_user
            )
            if created:
                return Response(
                    {'detail': 'Successfully subscribed.'},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'detail': 'Already subscribed.'},
                status=status.HTTP_200_OK
            )


class UserSubscriptionsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = UserGETSerializer
    permission_classes = [UsersAuthPermission]

    def get_queryset(self):
        return self.request.user.subscriptions.all()
