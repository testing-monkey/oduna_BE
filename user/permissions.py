from rest_framework.permissions import BasePermission

from user.choices import UserType


class OwnProfilePermission(BasePermission):
    message = "Not Object Owner."
    """
    Object-level permission to only allow updating his own profile
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class SuperAdminPermission(BasePermission):
    message = "Admin User Only."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.is_superuser)


class AdminPermission(BasePermission):
    message = "Not Object Owner."
    """
    Object-level permission to only allow updating his own profile
    """

    def has_permission(self, request, view):
        is_permitted = bool(
            request.user.is_authenticated and request.user.user_type == UserType.ADMIN
        )
        return is_permitted
class DeveloperPermission(BasePermission):
    message = "Not Object Owner."
    """
    Object-level permission to only allow updating his own profile
    """

    def has_permission(self, request, view):
        is_permitted = bool(
            request.user and request.user.user_type == UserType.DEVELOPER
        )
        return is_permitted
