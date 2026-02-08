from rest_framework import serializers

from accounts.models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        read_only_fields = ["id"]
        fields = [
            "id",
            "name",
            "description",
        ]

    def validate_name(self, value):
        """
        API-level validation for better error messages.
        """

        if value:
            cleaned = value.strip().lower()
        else:
            cleaned = None

        if not cleaned:
            raise serializers.ValidationError("Department name cannot be empty.")
        if len(cleaned) < 2:
            raise serializers.ValidationError(
                "Department name must be at least 2 characters."
            )
        if len(cleaned) > 100:
            raise serializers.ValidationError(
                "Department name must be at most 100 characters."
            )

        # Case-insensitive uniqueness check
        qs = Department.objects.filter(name__iexact=cleaned)
        if self.instance:  # If updating
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A department with this name already exists."
            )

        return cleaned

    def validate_description(self, value):
        if value:
            cleaned = value.strip()
            if not cleaned:
                return None

            if len(cleaned) > 500:
                raise serializers.ValidationError(
                    "Department description cannot exceed 500 characters."
                )

            return cleaned

        return None
