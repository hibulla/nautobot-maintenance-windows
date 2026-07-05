"""Choice constants for nautobot_maintenance_windows."""

from django.db import models


class MaintenanceWindowTypeChoices(models.TextChoices):
    """Supported maintenance window types."""

    MAINTENANCE = "MAINTENANCE", "Maintenance"
    EXCLUSION = "EXCLUSION", "Exclusion"


class MaintenanceStateChoices(models.TextChoices):
    """Evaluation states returned by the plugin."""

    IN_MAINTENANCE = "IN_MAINTENANCE", "In maintenance"
    IN_EXCLUSION = "IN_EXCLUSION", "In exclusion"
    NONE = "NONE", "None"


class ChangeValidationResultChoices(models.TextChoices):
    """Change validation outcomes."""

    ALLOWED = "ALLOWED", "Allowed"
    BLOCKED = "BLOCKED", "Blocked"
    WARN = "WARN", "Warn"


DAY_OF_WEEK_CHOICES = (
    (0, "Monday"),
    (1, "Tuesday"),
    (2, "Wednesday"),
    (3, "Thursday"),
    (4, "Friday"),
    (5, "Saturday"),
    (6, "Sunday"),
)

UTC_TIMEZONE = "UTC"
