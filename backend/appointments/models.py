# appointments/models.py

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.models.user import User
from appointments.enum import Status


class Appointment(models.Model):
    """
    Appointment model for hospital care system.
    - Each appointments links exactly one patient and one doctor.
    - Only patients can create appointments; patients and doctors can update/cancel.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments_as_patient",
        help_text="The patient who booked the appointments",
    )
    doctor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments_as_doctor",
        help_text="The doctor for this appointments",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED
    )
    reason = models.TextField(
        blank=True, null=True, help_text="Optional reason for visit"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["start_time"]

    def clean(self):
        """Custom validation for appointments"""
        # Ensure start_time < end_time
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

        # Prevent overlapping appointments for the same doctor
        overlapping = Appointment.objects.filter(
            doctor=self.doctor,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )
        # Exclude self if updating existing appointments
        if self.pk:
            overlapping = overlapping.exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(
                "Doctor already has an overlapping appointments at this time."
            )

        # Optional: Ensure appointments is in the future
        if self.start_time < timezone.now():
            raise ValidationError("Appointment start time must be in the future.")

        if self.reason:
            self.description = self.reason.strip()
        if not self.reason:
            self.reason = None
        if self.reason and len(self.reason) > 500:
            raise ValidationError(
                {"reason": "Appointment reason cannot exceed 500 characters."}
            )

    def __str__(self):
        return f"{self.patient} → {self.doctor} at {self.start_time.strftime('%Y-%m-%d %H:%M')}"  # noqa: E501
