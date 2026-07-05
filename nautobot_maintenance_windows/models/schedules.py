"""MaintenanceWindowSchedule model."""

from django.core.exceptions import ValidationError
from django.db import models
from nautobot.apps.models import BaseModel

from nautobot_maintenance_windows.choices import DAY_OF_WEEK_CHOICES, UTC_TIMEZONE


class MaintenanceWindowSchedule(BaseModel):
    """UTC weekly schedule recurrence for a MaintenanceWindow."""

    is_metadata_associable_model = False

    maintenance_window = models.ForeignKey(
        to="nautobot_maintenance_windows.MaintenanceWindow",
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    start_day_of_week = models.PositiveSmallIntegerField(choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField(help_text="UTC time only.")
    end_day_of_week = models.PositiveSmallIntegerField(choices=DAY_OF_WEEK_CHOICES)
    end_time = models.TimeField(help_text="UTC time only.")
    timezone = models.CharField(max_length=3, default=UTC_TIMEZONE, editable=False)

    class Meta:
        """Meta attributes."""

        ordering = ["maintenance_window__name", "start_day_of_week", "start_time"]
        unique_together = (
            "maintenance_window",
            "start_day_of_week",
            "start_time",
            "end_day_of_week",
            "end_time",
        )
        constraints = (
            models.CheckConstraint(
                check=models.Q(start_day_of_week__gte=0) & models.Q(start_day_of_week__lte=6),
                name="maintenance_windows_start_day_0_6",
            ),
            models.CheckConstraint(
                check=models.Q(end_day_of_week__gte=0) & models.Q(end_day_of_week__lte=6),
                name="maintenance_windows_end_day_0_6",
            ),
            models.CheckConstraint(check=models.Q(timezone=UTC_TIMEZONE), name="maintenance_windows_timezone_utc"),
            models.CheckConstraint(
                check=~models.Q(
                    start_day_of_week=models.F("end_day_of_week"),
                    start_time=models.F("end_time"),
                ),
                name="maintenance_windows_start_end_not_equal",
            ),
        )
        verbose_name = "Maintenance Window Schedule"
        verbose_name_plural = "Maintenance Window Schedules"

    def __str__(self):
        """Stringify instance."""
        return (
            f"{self.maintenance_window}: {self.get_start_day_of_week_display()} {self.start_time} UTC - "
            f"{self.get_end_day_of_week_display()} {self.end_time} UTC"
        )

    def clean(self):
        """Validate normalized UTC schedule fields."""
        super().clean()
        if self.timezone != UTC_TIMEZONE:
            raise ValidationError({"timezone": "Maintenance window schedules must use UTC."})
        if self.start_day_of_week == self.end_day_of_week and self.start_time == self.end_time:
            raise ValidationError("Schedule start and end must not be identical.")

    def save(self, *args, **kwargs):
        """Persist with the non-configurable UTC timezone constant."""
        self.timezone = UTC_TIMEZONE
        super().save(*args, **kwargs)
