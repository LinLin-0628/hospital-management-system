# appointments/serializers.py

from django.utils import timezone
from rest_framework import serializers

from accounts.models import User
from accounts.serializers.user import UserShortReadSerializer
from appointments.enum import Status
from appointments.models import Appointment


# --------------------------
# WRITE SERIALIZER
# --------------------------
class AppointmentWriteSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="patient"),
        required=False,  # patient is usually assigned from request.user in ViewSet
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="doctor")
    )
    status = serializers.ChoiceField(choices=Status.choices, default=Status.SCHEDULED)
    reason = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "start_time", "end_time", "status", "reason"]

    def validate(self, attrs):
        start_time = attrs.get("start_time")
        end_time = attrs.get("end_time")
        doctor = attrs.get("doctor")

        if start_time >= end_time:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
            )

        if start_time < timezone.now():
            raise serializers.ValidationError(
                {"start_time": "Appointment start time must be in the future."}
            )

        # Prevent overlapping appointments for the same doctor
        overlapping = Appointment.objects.filter(
            doctor=doctor, start_time__lt=end_time, end_time__gt=start_time
        )
        if self.instance:
            overlapping = overlapping.exclude(pk=self.instance.pk)
        if overlapping.exists():
            raise serializers.ValidationError(
                {
                    "doctor": "Doctor already has an overlapping appointment at this time."  # noqa: E501
                }
            )

        return attrs

    def validate_reason(self, value):
        if value:
            cleaned = value.strip()
            if not cleaned:
                return None

            if len(cleaned) > 500:
                raise serializers.ValidationError(
                    "Appointment reason cannot exceed 500 characters."
                )

            return cleaned

        return None

    def create(self, validated_data):
        """
        Patient is assigned automatically in the ViewSet before serializer.save()
        """
        return super().create(validated_data)


# --------------------------
# READ SERIALIZER
# --------------------------
class AppointmentReadSerializer(serializers.ModelSerializer):
    patient = UserShortReadSerializer(read_only=True)
    doctor = UserShortReadSerializer(read_only=True)
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
            "start_time",
            "end_time",
            "status",
            "reason",
            "created_at",
            "updated_at",
        ]
