from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class UserAdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin' or request.user.is_staff
