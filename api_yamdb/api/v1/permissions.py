from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Правом редактирования контента наделены только авторы."""

    message = 'Вы не являетесь автором изменяемого контента!'

    def has_object_permission(self, request, view, review):
        return (
            request.method in permissions.SAFE_METHODS
            or review.author == request.user
        )