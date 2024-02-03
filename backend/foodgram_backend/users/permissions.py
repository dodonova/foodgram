import logging
from venv import logger

from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)

logging.basicConfig(level=logging.INFO)


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


class IsAuthorOrSafeMethods(IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        logger.info(f"~~~~~ CHECK PERMISSION IsAuthorOrSafeMethods\n")
        logger.info(f"~~~~~ {view.action}")
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            # or request.user.role == User.MODERATOR
            or request.user.is_admin
        )


class RecipeActionsPermission(BasePermission):
    def has_permission(self, request, view):
        logger.info(f"ACTION: {view.action}")

        return (request.user.is_authenticated
                or view.action in ('list', 'retrieve'))

    def has_object_permission(self, request, view, obj):
        logger.info(f"OBJECT ACTION: {view.action}")

        if view.action in ('update', 'partial_update', 'destroy'):
            return (obj.author == request.user
                    or request.user.is_admin)

        return (request.user.is_authenticated
                or view.action in ('list', 'retrieve'))


# class UsersAuthPermission(IsAuthenticatedOrReadOnly):
#     pass

class UsersAuthPermission(BasePermission):
    def has_permission(self, request, view):
        return (
            view.action in ('create', 'token_login',
                            'list', 'retrieve')
            or request.user.is_authenticated
        )