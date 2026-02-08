from rest_framework import serializers

from accounts.models import Department, Specialization
from accounts.serializers.department import DepartmentSerializer


class SpecializationReadSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = Specialization
        fields = [
            "id",
            "name",
            "department",
            "description",
        ]


class SpecializationWriteSerializer(serializers.ModelSerializer):
    department_id = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.all(), source="department"
    )

    class Meta:
        model = Specialization
        fields = [
            "name",
            "department_id",
            "description",
        ]

    def validate_name(self, value):
        """
        API-level validation for name
        """
        cleaned = value.strip().lower()
        if not cleaned:
            raise serializers.ValidationError("Specialization name cannot be empty.")
        if len(cleaned) < 2:
            raise serializers.ValidationError(
                "Specialization name must be at least 2 characters."
            )
        if len(cleaned) > 100:
            raise serializers.ValidationError(
                "Specialization name must be at most 100 characters."
            )

        # Check uniqueness per department
        department = self.initial_data.get("department_id") or getattr(
            self.instance, "department_id", None
        )
        if department:
            qs = Specialization.objects.filter(
                name__iexact=cleaned, department_id=department
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "A specialization with this name already exists in this department."
                )

        return cleaned

    def validate_description(self, value):
        if value:
            cleaned = value.strip()
            if not cleaned:
                return None

            if len(cleaned) > 500:
                raise serializers.ValidationError(
                    "Specialization description cannot exceed 500 characters."
                )

            return cleaned

        return None
