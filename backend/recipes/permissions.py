from rest_framework import permissions


class AdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ для аутентифицированных
    пользователей с правами администратора
    для всех методов, кроме POST, PUT и DELETE.
    """

    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь права администратора
        или запрашивается безопасный метод.
        """
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь права администратора
        или запрашивается безопасный метод.
        """
        return self.has_permission(request, view)
