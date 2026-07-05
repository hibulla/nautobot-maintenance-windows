"""MaintenanceWindow model."""

from django.db import models
from nautobot.apps.constants import CHARFIELD_MAX_LENGTH
from nautobot.apps.models import OrganizationalModel, extras_features

from nautobot_maintenance_windows.choices import MaintenanceWindowTypeChoices


@extras_features(
    "custom_fields",
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "relationships",
    "webhooks",
)
class MaintenanceWindow(OrganizationalModel):
    """Global maintenance or exclusion window assignable to many devices."""

    name = models.CharField(max_length=CHARFIELD_MAX_LENGTH, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    window_type = models.CharField(
        max_length=32,
        choices=MaintenanceWindowTypeChoices.choices,
        default=MaintenanceWindowTypeChoices.MAINTENANCE,
    )
    devices = models.ManyToManyField(
        to="dcim.Device",
        through="nautobot_maintenance_windows.DeviceMaintenanceWindowAssignment",
        related_name="maintenance_windows",
        blank=True,
    )

    natural_key_field_names = ["name"]

    class Meta:
        """Meta attributes."""

        ordering = ["name"]
        verbose_name = "Maintenance Window"
        verbose_name_plural = "Maintenance Windows"

    def __str__(self):
        """Stringify instance."""
        return self.name
