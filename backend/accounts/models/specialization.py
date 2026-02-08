from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower

from accounts.models.department import Department


class Specialization(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name="specializations"
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                "department",
                name="unique_specialization_per_department_ci",
            )
        ]

    def clean(self):
        """
        Model-level cleaning and validation
        """
        # --- Name ---
        if self.name:
            self.name = self.name.strip().lower()
        if not self.name:
            raise ValidationError({"name": "Specialization name cannot be empty."})
        if len(self.name) < 2:
            raise ValidationError(
                {"name": "Specialization name must be at least 2 characters."}
            )
        if len(self.name) > 100:
            raise ValidationError(
                {"name": "Specialization name must be at most 100 characters."}
            )

        # --- Department ---
        if not self.department:
            raise ValidationError({"department": "Department must be specified."})

        # --- Description ---
        if self.description:
            self.description = self.description.strip()
        if not self.description:
            self.description = None
        if self.description and len(self.description) > 500:
            raise ValidationError(
                {
                    "description": "Specialization description cannot exceed 500 characters."  # noqa: E501
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name.title()} ({self.department.name.title()})"
