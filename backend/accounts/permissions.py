from rest_framework.permissions import BasePermission

from accounts.models.enum import UserRole


class IsNonAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == UserRole.ADMIN


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if view.action in ["list", "retrieve"]:
            return request.user.is_authenticated

        return request.user.is_authenticated and request.user.role == UserRole.ADMIN
