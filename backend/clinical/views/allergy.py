from rest_framework import viewsets

from accounts.permissions import IsAdminOrReadOnly
from clinical.models.allergy import Allergy
from clinical.serializers.allergy import AllergySerializer


class AllergyViewSet(viewsets.ModelViewSet):
    queryset = Allergy.objects.all().order_by("name")
    serializer_class = AllergySerializer
    permission_classes = [IsAdminOrReadOnly]
