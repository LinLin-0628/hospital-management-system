from rest_framework import mixins, status, viewsets
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from accounts.models.enum import UserRole
from accounts.models.user import User
from accounts.permissions import IsAdmin, IsNonAuthenticated
from accounts.serializers.user import UserNestedWriteSerializer, UserReadSerializer


class IsAdminOrUserModelOwnerOnly(BasePermission):
    def has_permission(self, request, view):
        # List and Create: Admin only
        if view.action in ["list", "create"]:
            return request.user.is_authenticated and request.user.role == UserRole.ADMIN

        # Retrieve: Any authenticated user (ownership checked at object level)
        if view.action == "retrieve":
            return request.user.is_authenticated

        # Update/Delete: Admin only
        if view.action in ["update", "partial_update", "destroy"]:
            return request.user.is_authenticated and request.user.role == UserRole.ADMIN

        return False

    # for user object
    # User can access their own account information (Or admin)
    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == UserRole.ADMIN:
            return True

        # For retrieve, allow owner
        if view.action == "retrieve":
            return obj.id == request.user.id

        # Update/Delete: Admin only (already checked in has_permission, but being explicit)  # noqa: E501
        return False


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
):
    queryset = (
        User.objects.select_related(
            "doctor_profile", "nurse_profile", "patient_profile"
        )
        .all()
        .order_by("username")
    )

    def get_serializer_class(self):
        if self.action in ["create"]:
            return UserNestedWriteSerializer

        return UserReadSerializer

    def get_permissions(self):
        if self.action in ["create"]:
            return [(IsNonAuthenticated | IsAdmin)()]

        return [IsAdminOrUserModelOwnerOnly()]

    def create(self, request, *args, **kwargs):
        write_serializer = self.get_serializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        user = write_serializer.save()

        # Now return using the read serializer
        read_serializer = UserReadSerializer(user)
        headers = self.get_success_headers(read_serializer.data)

        return Response(
            read_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )
