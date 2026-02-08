from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    DOCTOR = "doctor", _("Doctor")
    NURSE = "nurse", _("Nurse")
    PATIENT = "patient", _("Patient")
    ADMIN = "admin", _("Admin")


class Gender(models.TextChoices):
    MALE = "male", _("Male")
    FEMALE = "female", _("Female")
    OTHER = "other", _("Other")
    UNKNOWN = "unknown", _("Unknown")
