from rest_framework import viewsets

from accounts.models.specialization import Specialization
from accounts.permissions import IsAdminOrReadOnly
from accounts.serializers.specialization import (
    SpecializationReadSerializer,
    SpecializationWriteSerializer,
)


class SpecializationViewSet(viewsets.ModelViewSet):
    queryset = (
        Specialization.objects.select_related("department").all().order_by("name")
    )
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return SpecializationReadSerializer
        return SpecializationWriteSerializer
