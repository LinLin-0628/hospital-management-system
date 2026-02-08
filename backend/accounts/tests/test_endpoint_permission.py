import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from accounts.models.enum import UserRole
from accounts.tests.factories.user import UserFactory
from accounts.views.user import UserViewSet

endpoint = "/api/v1/users/"


@pytest.mark.parametrize(
    "role, expected_status_code",
    [
        pytest.param(UserRole.ADMIN, status.HTTP_200_OK, id="admin"),
        pytest.param(UserRole.DOCTOR, status.HTTP_403_FORBIDDEN, id="doctor"),
        pytest.param(UserRole.NURSE, status.HTTP_403_FORBIDDEN, id="nurse"),
        pytest.param(UserRole.PATIENT, status.HTTP_403_FORBIDDEN, id="patient"),
        pytest.param("anonymous", status.HTTP_401_UNAUTHORIZED, id="anonymous"),
    ],
)
def test_list_users_permission(mocker, role, expected_status_code):
    user_view = UserViewSet.as_view({"get": "list"})
    request = APIRequestFactory().get(endpoint)

    if role == "anonymous":
        request.user = AnonymousUser()
    else:
        user = UserFactory.build(role=role)
        force_authenticate(request, user=user)

    mocker.patch.object(UserViewSet, "queryset", new=mocker.MagicMock())

    response = user_view(request)

    assert response.status_code == expected_status_code
