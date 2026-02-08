import uuid
from datetime import date

from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.functions import Lower

from accounts.models.department import Department
from accounts.models.enum import Gender, UserRole
from accounts.models.specialization import Specialization
from clinical.models.enum import BloodGroup

identity_card_number_validator = RegexValidator(
    regex=r"^\d{6}-\d{2}-\d{4}$",
    message="Identity card number must be in the format XXXXXX-XX-XXXX",
)


class User(AbstractUser):
    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("username"), name="unique_user_username_ci")
        ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=10, choices=UserRole.choices, blank=True, null=True
    )
    gender = models.CharField(
        max_length=10, choices=Gender.choices, default=Gender.UNKNOWN
    )

    def clean(self):
        # Trim and normalize username
        if self.username:
            self.username = self.username.strip()
        if not self.username or len(self.username) < 3:
            raise ValidationError(
                {"username": "Username must be at least 3 characters."}
            )

        # Trim and normalize first/last name
        if self.first_name:
            self.first_name = self.first_name.strip()
        if self.last_name:
            self.last_name = self.last_name.strip()

        # Normalize email
        if self.email:
            self.email = self.email.strip().lower()

        # Role validation
        if self.is_superuser:
            self.role = UserRole.ADMIN

        if self.role not in [role[0] for role in UserRole.choices]:
            raise ValidationError({"role": f"Invalid role: {self.role}"})

        # Gender validation handled by choices

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="doctor_profile"
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, related_name="doctors"
    )
    specialization = models.ForeignKey(
        Specialization, on_delete=models.SET_NULL, null=True, related_name="doctors"
    )
    license_number = models.CharField(max_length=50, unique=True)

    def clean(self):
        # Ensure user role is doctor
        if self.user.role != UserRole.DOCTOR:
            raise ValidationError(
                {"user": "User role must be doctor to create DoctorProfile."}
            )
        # Trim license_number
        if self.license_number:
            self.license_number = self.license_number.strip()
        if not self.license_number:
            raise ValidationError({"license_number": "License number cannot be empty."})
        if len(self.license_number) > 50:
            raise ValidationError(
                {"license_number": "License number max length is 50 characters."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class NurseProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="nurse_profile"
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, related_name="nurses"
    )

    def clean(self):
        if self.user.role != UserRole.NURSE:
            raise ValidationError(
                {"user": "User role must be nurse to create NurseProfile."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Nurse {self.user.get_full_name()}"


class PatientProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="patient_profile"
    )
    date_of_birth = models.DateField(null=True, blank=True)
    identity_card_number = models.CharField(
        max_length=14, unique=True, validators=[identity_card_number_validator]
    )
    allergies = models.ManyToManyField(
        "clinical.Allergy", blank=True, related_name="patients"
    )
    blood_group = models.CharField(
        max_length=10, choices=BloodGroup.choices, null=True, blank=True
    )

    def clean(self):
        # Ensure user role
        if self.user.role != UserRole.PATIENT:
            raise ValidationError(
                {"user": "User role must be patient to create PatientProfile."}
            )

        # DOB validation
        if self.date_of_birth and self.date_of_birth > date.today():
            raise ValidationError(
                {"date_of_birth": "Date of birth cannot be in the future."}
            )

        # Trim and validate identity_card_number
        if self.identity_card_number:
            self.identity_card_number = self.identity_card_number.strip()

        # Blood group validation handled by choices

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def age(self):
        if not self.date_of_birth:
            return {
                "years": None,
                "months": None,
                "full_text": None,
            }

        today = date.today()

        # Guard against bad data (DOB in the future)
        if self.date_of_birth > today:
            return {
                "years": 0,
                "months": 0,
                "full_text": "0y 0m",
            }

        diff = relativedelta(today, self.date_of_birth)

        return {
            "years": diff.years,
            "months": diff.months,
            "full_text": f"{diff.years}y {diff.months}m",
        }

    def __str__(self):
        return f"Patient {self.user.get_full_name()}"
