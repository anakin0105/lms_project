from rest_framework.permissions import BasePermission

class IsModer(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='moders').exists()

class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.groups.filter(name='moders').exists():
            return True
        return obj.owner == request.user