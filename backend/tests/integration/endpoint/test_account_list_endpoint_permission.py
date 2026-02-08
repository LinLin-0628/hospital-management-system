import pytest
from rest_framework import status

endpoint = "/api/v1/users/"


@pytest.mark.parametrize(
    "client_fixture, expected_status_code",
    [
        pytest.param("admin_client", status.HTTP_200_OK, id="admin"),
        pytest.param("doctor_client", status.HTTP_403_FORBIDDEN, id="doctor"),
        pytest.param("nurse_client", status.HTTP_403_FORBIDDEN, id="nurse"),
        pytest.param("patient_client", status.HTTP_403_FORBIDDEN, id="patient"),
        pytest.param(
            "unauthorized_client", status.HTTP_401_UNAUTHORIZED, id="unauthorized"
        ),
    ],
)
def test_list_users(request, client_fixture, expected_status_code):
    api_client = request.getfixturevalue(client_fixture)
    response = api_client.get(endpoint)

    assert response.status_code == expected_status_code
