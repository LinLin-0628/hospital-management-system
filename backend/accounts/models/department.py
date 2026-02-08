from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.functions import Lower


class Department(models.Model):
    NAME_MIN_LEN = 2
    NAME_MAX_LEN = 100
    DESC_MAX_LEN = 500

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            # Case-insensitive uniqueness
            models.UniqueConstraint(
                Lower("name"),
                name="unique_department_name_ci",
            )
        ]

    def clean(self):
        # --- Name ---
        if self.name:
            self.name = self.name.strip().lower()
        if not self.name:
            raise ValidationError({"name": "Department name cannot be empty."})
        if len(self.name) < self.NAME_MIN_LEN:
            raise ValidationError(
                {"name": "Department name must be at least 2 characters."}
            )
        if len(self.name) > self.NAME_MAX_LEN:
            raise ValidationError(
                {"name": "Department name must be at most 100 characters."}
            )

        # --- Description ---
        if self.description:
            self.description = self.description.strip()
        if not self.description:
            self.description = None
        if self.description and len(self.description) > self.DESC_MAX_LEN:
            raise ValidationError(
                {"description": "Department description cannot exceed 500 characters."}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name.title()

    def __repr__(self):
        return f"<{self.__class__.__name__}(pk={self.pk}, name={self.name!r})>"
