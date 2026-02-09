from django.db import models
from django.utils.translation import gettext_lazy as _


class Status(models.TextChoices):
    SCHEDULED = "scheduled", _("Scheduled")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")
    NO_SHOW = "no_show", _("No-show")
