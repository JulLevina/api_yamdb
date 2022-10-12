from rest_framework import permissions


class ReadOnly(permissions.BasePermission):
    """Правом создания контента наделен только администратор."""

    message = (
        'Для создания контента необходимо '
        'обладать правами администратора.'
    )

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    """Правом управления контентом наделен только администратор или автор."""

    message = (
        'Для создания контента необходимо '
        'обладать правами администратора или автора.')

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.role == 'admin'
            or request.user.role == 'moderator'
            or request.user.is_superuser
        )


class AdminOnly(permissions.BasePermission):
    """Права только для администратора."""
    message = 'Только для администратора!'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.role == 'admin'
                 or request.user.is_superuser)
        )
