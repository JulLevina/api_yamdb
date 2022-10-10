from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Правом редактирования контента наделены только авторы."""

    message = 'Вы не являетесь автором изменяемого контента!'

    # def has_permission(self, request, view):
    #     (request.method in permissions.SAFE_METHODS
    #             or (request.user.is_authenticated
    #                 and request.user.role == 'user'))
    
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class ReadOnly(permissions.BasePermission):
    """Правом создания контента наделен только администратор."""

    message = (
        'Для создания контента необходимо '
        'обладать правами администратора')

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsStaffOrReadOnly(permissions.BasePermission):
    """Правом создания контента наделен только администратор."""

    message = (
        'Для создания контента необходимо '
        'обладать правами администратора')

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.role == 'admin'))
  

class AdminOnly(permissions.BasePermission):
    """Права только для администратора."""
    message = 'Только для администратора!'

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and (request.user.role == 'admin' or
                     request.user.is_superuser))
