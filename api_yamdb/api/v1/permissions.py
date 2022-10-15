from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """Предоставление пользователям права чтения контента."""

    message = 'Вам предоставлено право чтения контента.'

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    """Права только для администратора, модератора, автора."""

    message = (
        'Для создания контента необходимо обладать '
        'правами администратора, модератора или автора.'
    )

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )


class AdminOnly(permissions.BasePermission):
    """Права только для администратора."""

    message = 'Только для администратора!'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
