from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)

from users.models import User


class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(IsAdmin):

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or super().has_permission(request, view)
        )


class IsAuthorModerAdminOrSafeMethods(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.role == User.MODERATOR
            or request.user.is_admin
        )


class UsersAuthPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            view.action in [
                'create',
                'token_login',
                'token_login_with_token'
            ]
            or request.user.is_authenticated
        )
