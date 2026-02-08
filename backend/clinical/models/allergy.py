from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower


class Allergy(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            # Case-insensitive uniqueness
            models.UniqueConstraint(
                Lower("name"),
                name="unique_allergy_name_ci",
            )
        ]

    def clean(self):
        """
        Model-level cleaning and validation.
        Ensures safe storage in DB.
        """
        # --- Name ---
        if self.name:
            self.name = self.name.strip().lower()
        if not self.name:
            raise ValidationError({"name": "Allergy name cannot be empty."})
        if len(self.name) < 2:
            raise ValidationError(
                {"name": "Allergy name must be at least 2 characters."}
            )
        if len(self.name) > 100:
            raise ValidationError(
                {"name": "Allergy name must be at most 100 characters."}
            )

        # --- Description ---
        if self.description:
            self.description = self.description.strip()
        if not self.description:
            self.description = None
        if self.description and len(self.description) > 500:
            raise ValidationError(
                {"description": "Allergy description cannot exceed 500 characters."}
            )

    def save(self, *args, **kwargs):
        """
        Ensure validation always runs.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        # Display-friendly title case
        return self.name.title()
