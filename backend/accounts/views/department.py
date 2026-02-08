from rest_framework import viewsets

from accounts.models.department import Department
from accounts.permissions import IsAdminOrReadOnly
from accounts.serializers.department import DepartmentSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by("name")
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
