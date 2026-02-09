# appointments/urls.py

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from appointments.views import AppointmentViewSet

# Create DRF router
router = DefaultRouter()
router.register(r"appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("", include(router.urls)),
]
