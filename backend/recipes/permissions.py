from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied


class AuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            raise PermissionDenied(detail='Нет доступа без авторизации.')
        return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            raise PermissionDenied(detail='Нет доступа без авторизации.')
        if request.user.is_staff or request.user == obj.author:
            return True
        raise PermissionDenied(detail='У вас нет прав для этого действия.')
