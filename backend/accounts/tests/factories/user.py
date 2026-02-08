import random
from datetime import date, timedelta

import factory
from django.contrib.auth.hashers import make_password
from factory.django import DjangoModelFactory

from accounts.models.enum import Gender, UserRole
from accounts.models.user import DoctorProfile, NurseProfile, PatientProfile, User
from accounts.tests.factories.department import DepartmentFactory
from accounts.tests.factories.specialization import SpecializationFactory
from clinical.models.enum import BloodGroup
from clinical.tests.factories.allergy import AllergyFactory


def generate_ic_number(n: int):
    """
    Produces valid XXXXXX-XX-XXXX format for patient.
    """
    birth = f"{(n % 90) + 10:02d}{(n % 12) + 1:02d}{(n % 28) + 1:02d}"
    middle = f"{n % 99:02d}"
    last = f"{n % 9999:04d}"
    return f"{birth}-{middle}-{last}"


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    password = factory.LazyFunction(lambda: make_password("testpass123"))
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    gender = Gender.UNKNOWN

    # Default role; can override when calling factory
    role = UserRole.PATIENT

    @factory.post_generation
    def create_profile(self, create, extracted, **kwargs):
        """
        Automatically creates the corresponding profile depending on user.role.
        Allows overriding profile fields via extracted dict:
            UserFactory(role=UserRole.DOCTOR, create_profile={'license_number': '123'})
        """
        if not create:
            return

        profile_data = extracted or {}

        if self.role == UserRole.DOCTOR:
            department = profile_data.pop("department", None) or DepartmentFactory()
            specialization = profile_data.pop(
                "specialization", None
            ) or SpecializationFactory(department=department)
            license_number = profile_data.pop(
                "license_number", f"LIC-{self.pk or 0:04d}"
            )
            DoctorProfile.objects.create(
                user=self,
                department=department,
                specialization=specialization,
                license_number=license_number,
                **profile_data,
            )

        elif self.role == UserRole.NURSE:
            department = profile_data.pop("department", None) or DepartmentFactory()
            NurseProfile.objects.create(
                user=self, department=department, **profile_data
            )

        elif self.role == UserRole.PATIENT:
            date_of_birth = profile_data.pop(
                "date_of_birth", date.today() - timedelta(days=365 * 20)
            )
            identity_card_number = profile_data.pop(
                "identity_card_number", generate_ic_number(self.pk or 0)
            )
            allergies = profile_data.pop("allergies", [AllergyFactory()])
            blood_group = profile_data.pop(
                "blood_group",
                random.choice(  # noqa: S311
                    [bg.value for bg in BloodGroup if bg != BloodGroup.UNKNOWN]
                ),
            )
            patient = PatientProfile.objects.create(
                user=self,
                date_of_birth=date_of_birth,
                identity_card_number=identity_card_number,
                blood_group=blood_group,
                **profile_data,
            )
            # Add allergies
            for allergy in allergies:
                patient.allergies.add(allergy)
