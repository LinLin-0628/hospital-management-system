# appointments/views.py


from rest_framework import permissions, viewsets

from appointments.models import Appointment
from appointments.serializers import (
    AppointmentReadSerializer,
    AppointmentWriteSerializer,
)


class IsPatientOrDoctor(permissions.BasePermission):
    """
    Custom permission:
    - Patient can create appointments
    - Patient or Doctor can update/cancel
    - Other roles have read-only access
    """

    def has_permission(self, request, view):
        # Everyone can list/retrieve
        if view.action in ["list", "retrieve"]:
            return True
        # Only patients can create
        if view.action == "create" and getattr(request.user, "role", None) == "patient":
            return True
        # Only patients or doctors can update/partial_update/destroy
        if view.action in ["update", "partial_update", "destroy"] and getattr(
            request.user, "role", None
        ) in ["patient", "doctor"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        # Read-only for everyone
        if view.action in ["retrieve"]:
            return True
        # Only patient who owns or doctor assigned can modify
        if view.action in ["update", "partial_update", "destroy"]:
            return obj.patient == request.user or obj.doctor == request.user
        return True


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all().order_by("start_time")

    permission_classes = [IsPatientOrDoctor]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AppointmentReadSerializer
        return AppointmentWriteSerializer

    def perform_create(self, serializer):
        # Automatically assign the logged-in patient as 'patient'
        serializer.save(patient=self.request.user)
