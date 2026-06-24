from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    """Модератор имеет доступ ко всему"""
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moders').exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

class IsOwner(BasePermission):
    """Владелец имеет доступ к своим объектам"""
    def has_permission(self, request, view):
        # Для создания — разрешаем, но в perform_create owner устанавливается
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.groups.filter(name='moders').exists():
            return True
        return getattr(obj, 'owner', None) == request.user


class IsModerOrOwner(BasePermission):
    """Модератор или владелец объекта"""
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.groups.filter(name='moders').exists():
            return True
        return getattr(obj, 'owner', None) == request.user