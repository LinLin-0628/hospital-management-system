from django.urls import include, path
from rest_framework.routers import DefaultRouter

from clinical.views.allergy import AllergyViewSet

router = DefaultRouter()
router.register(r"allergies", AllergyViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
