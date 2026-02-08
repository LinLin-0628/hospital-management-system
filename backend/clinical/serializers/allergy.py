from rest_framework import serializers

from clinical.models.allergy import Allergy


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        read_only_fields = ["id"]
        fields = [
            "id",
            "name",
            "description",
        ]

    def validate_name(self, value):
        """
        API-level validation for allergy name.
        """
        cleaned = value.strip().lower()

        if not cleaned:
            raise serializers.ValidationError("Allergy name cannot be empty.")
        if len(cleaned) < 2:
            raise serializers.ValidationError(
                "Allergy name must be at least 2 characters."
            )
        if len(cleaned) > 100:
            raise serializers.ValidationError(
                "Allergy name must be at most 100 characters."
            )

        # Case-insensitive uniqueness check
        qs = Allergy.objects.filter(name__iexact=cleaned)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError(
                "An allergy with this name already exists."
            )

        return cleaned

    def validate_description(self, value):
        """
        API-level validation for description.
        """
        if value:
            cleaned = value.strip()
            if not cleaned:
                return None
            if len(cleaned) > 500:
                raise serializers.ValidationError(
                    "Allergy description cannot exceed 500 characters."
                )
            return cleaned
        return None
