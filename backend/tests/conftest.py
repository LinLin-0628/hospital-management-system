from pathlib import Path

import pytest
from rest_framework.test import APIClient

from accounts.models.enum import UserRole
from accounts.tests.factories.user import UserFactory


def pytest_collection_modifyitems(config, items):
    for item in items:
        test_path = Path(item.nodeid.split("::")[0])  # Get just the file path part

        if "integration" in test_path.parts:
            item.add_marker(pytest.mark.integration)

        elif "e2e" in test_path.parts:
            item.add_marker(pytest.mark.e2e)


@pytest.fixture
def admin_client(db):
    """
    Authenticated client for admin user.
    """
    user = UserFactory(role=UserRole.ADMIN)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def doctor_client(db):
    """
    Authenticated client for doctor user.
    """
    user = UserFactory(role=UserRole.DOCTOR)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def nurse_client(db):
    """
    Authenticated client for nurse user.
    """
    user = UserFactory(role=UserRole.NURSE)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def patient_client(db):
    """
    Authenticated client for patient user.
    """
    user = UserFactory(role=UserRole.PATIENT)
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def unauthorized_client(db):
    """
    A client with no authentication, useful for testing permission errors.
    """
    return APIClient()
