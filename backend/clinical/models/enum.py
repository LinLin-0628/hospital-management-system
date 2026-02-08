from django.db import models
from django.utils.translation import gettext_lazy as _


class BloodGroup(models.TextChoices):
    A_POS = "a_pos", _("A+")
    A_NEG = "a_neg", _("A-")
    B_POS = "b_pos", _("B+")
    B_NEG = "b_neg", _("B-")
    AB_POS = "ab_pos", _("AB+")
    AB_NEG = "ab_neg", _("AB-")
    O_POS = "o_pos", _("O+")
    O_NEG = "o_neg", _("O-")
    UNKNOWN = "unknown", _("Unknown")
