from django.urls import include, path
from rest_framework.routers import DefaultRouter

from accounts.views.department import DepartmentViewSet
from accounts.views.specialization import SpecializationViewSet
from accounts.views.user import UserViewSet

router = DefaultRouter()
router.register(r"departments", DepartmentViewSet)
router.register(r"specializations", SpecializationViewSet)
router.register(r"users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
