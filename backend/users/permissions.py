from rest_framework.permissions import BasePermission

from .models import User


class IsAdmin(BasePermission):
    """Hanya user yang sudah login dan berrole admin (T3.7)."""

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.role == User.Role.ADMIN)
